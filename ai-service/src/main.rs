mod llm_client;
mod opensearch_ingest;

use llm_client::{LlmClient, RuntimeError};

use redis::AsyncCommands;
use redis::streams::{StreamReadOptions, StreamReadReply};
use serde_json::Value as JsonValue;
use std::{sync::Arc, time::Duration};
use tokio::{signal, sync::watch, task::JoinSet};
use tracing::{error, info};
use tracing_subscriber::prelude::*;

const SERVICE_NAME: &str = "ai-workers";

#[derive(Clone)]
struct AppState {
    redis: redis::Client,
    llm: Arc<LlmClient>,
}

#[derive(Clone, Debug)]
struct Settings {
    redis_url: String,
    ai_base_url: String,
    ai_model: String,
    ai_api_key: Option<String>,
    ai_workers: usize,
    ai_timeout_s: u64,
    xread_count: usize,
    result_stream_maxlen: Option<usize>,
    
    // Stream names
    tasks_stream: String,
    results_stream: String,
    consumer_group: String,

    // Logging
    log_level: String,
}

impl Settings {
    fn from_env() -> Self {
        fn env_string(name: &str, default: &str) -> String {
            std::env::var(name).unwrap_or_else(|_| default.to_string())
        }
        fn env_opt_string(name: &str) -> Option<String> {
            std::env::var(name).ok().and_then(|s| {
                let t = s.trim().to_string();
                if t.is_empty() { None } else { Some(t) }
            })
        }
        fn env_usize(name: &str, default: usize) -> usize {
            std::env::var(name)
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(default)
        }
        fn env_u64(name: &str, default: u64) -> u64 {
            std::env::var(name)
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(default)
        }
        fn env_opt_usize(name: &str) -> Option<usize> {
            std::env::var(name).ok().and_then(|v| {
                let t = v.trim();
                if t.is_empty() { None } else { t.parse().ok() }
            })
        }

        Self {
            redis_url: env_string("REDIS_URL", "redis://localhost:6379"),
            ai_base_url: env_string("AI_BASE_URL", "http://localhost:11434"),
            ai_model: env_string("AI_MODEL", "llama3"),
            ai_api_key: env_opt_string("AI_API_KEY"),
            ai_workers: env_usize("AI_WORKERS", 4),
            ai_timeout_s: env_u64("AI_TIMEOUT_S", 30),
            xread_count: env_usize("AI_XREAD_COUNT", 5),
            result_stream_maxlen: env_opt_usize("AI_RESULTS_MAXLEN"),
            
            tasks_stream: env_string("TASKS_STREAM", "ai:tasks"),
            results_stream: env_string("RESULTS_STREAM", "ai:results"),
            consumer_group: env_string("CONSUMER_GROUP", "ai-workers"),

            log_level: env_string("LOG_LEVEL", "info"),
        }
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    dotenv::dotenv().ok();

    // Best-effort bridge: log -> tracing (do not panic if already set)
    let _ = tracing_log::LogTracer::init();

    let cfg = Settings::from_env();

    // RUST_LOG overrides cfg.log_level (handy in docker / k8s)
    let filter = if let Ok(env) = std::env::var("RUST_LOG") {
        tracing_subscriber::EnvFilter::new(env)
    } else {
        tracing_subscriber::EnvFilter::new(cfg.log_level.clone())
    };

    // Optional OpenSearch ingest
    let ingest_url = std::env::var("OS_INGEST_URL")
        .ok()
        .filter(|v| !v.trim().is_empty());

    let os_handle = if let Some(url) = ingest_url {
        let (layer, handle) =
            opensearch_ingest::opensearch_ingest_layer(opensearch_ingest::OpenSearchIngestConfig {
                ingest_url: url,
                service_name: SERVICE_NAME.to_string(),
                ..Default::default()
            });

        let _ = tracing_subscriber::registry()
            .with(tracing_subscriber::fmt::layer().with_target(false))
            .with(filter)
            .with(layer)
            .try_init();

        Some(handle)
    } else {
        let _ = tracing_subscriber::registry()
            .with(tracing_subscriber::fmt::layer().with_target(false))
            .with(filter)
            .try_init();

        None
    };

    info!("starting {SERVICE_NAME}…");

    let redis_client = redis::Client::open(cfg.redis_url.clone())?;
    ensure_group(redis_client.clone(), &cfg.tasks_stream, &cfg.consumer_group).await?;
    let _ = ensure_group(redis_client.clone(), &cfg.results_stream, "result-readers").await;

    let http = reqwest::Client::builder()
        .timeout(Duration::from_secs(cfg.ai_timeout_s))
        .build()?;

    let llm = LlmClient {
        base_url: cfg.ai_base_url.clone(),
        model: cfg.ai_model.clone(),
        api_key: cfg.ai_api_key.clone(),
        http,
    };

    let state = AppState {
        redis: redis_client,
        llm: Arc::new(llm),
    };

    let (shutdown_tx, shutdown_rx) = watch::channel(false);

    let mut joinset = JoinSet::new();
    for i in 0..cfg.ai_workers {
        let st = state.clone();
        let cfg2 = cfg.clone();
        let consumer = format!("worker-{}", i + 1);
        let rx = shutdown_rx.clone();
        joinset.spawn(async move {
            worker_loop(st, cfg2, consumer, rx).await;
        });
    }

    shutdown_signal().await;
    info!("shutdown signal received; stopping workers...");
    let _ = shutdown_tx.send(true);

    while let Some(res) = joinset.join_next().await {
        if let Err(e) = res {
            error!("worker task join error: {e}");
        }
    }

    // ✅ Graceful flush on shutdown (best-effort)
    if let Some(h) = os_handle {
        h.shutdown().await;
    }

    Ok(())
}

async fn shutdown_signal() {
    let _ = signal::ctrl_c().await;
}

async fn ensure_group(
    redis_client: redis::Client,
    stream: &str,
    group: &str,
) -> Result<(), RuntimeError> {
    let mut conn = redis_client.get_multiplexed_async_connection().await?;

    let res: redis::RedisResult<String> = redis::cmd("XGROUP")
        .arg("CREATE")
        .arg(stream)
        .arg(group)
        .arg("0")
        .arg("MKSTREAM")
        .query_async::<String>(&mut conn)
        .await;

    match res {
        Ok(_) => {
            info!("created consumer group {group} on {stream}");
            Ok(())
        }
        Err(e) => {
            let s = e.to_string();
            if s.contains("BUSYGROUP") {
                Ok(())
            } else {
                Err(e.into())
            }
        }
    }
}

async fn worker_loop(
    state: AppState,
    cfg: Settings,
    consumer: String,
    shutdown_rx: watch::Receiver<bool>,
) {
    info!("[{consumer}] started");

    let mut conn: redis::aio::MultiplexedConnection =
        match state.redis.get_multiplexed_async_connection().await {
            Ok(c) => c,
            Err(e) => {
                error!("[{consumer}] redis connect failed: {e}");
                return;
            }
        };

    let opts_new = StreamReadOptions::default()
        .group(&cfg.consumer_group, &consumer)
        .count(cfg.xread_count);

    let opts_pending = StreamReadOptions::default()
        .group(&cfg.consumer_group, &consumer)
        .count(cfg.xread_count);

    let mut tick: u64 = 0;

    loop {
        if *shutdown_rx.borrow() {
            info!("[{consumer}] stopping");
            return;
        }

        tick = tick.wrapping_add(1);

        let mut reply: StreamReadReply =
            match conn.xread_options(&[cfg.tasks_stream.as_str()], &[">"], &opts_new).await {
                Ok(r) => r,
                Err(e) => {
                    error!("[{consumer}] xreadgroup error: {e}");
                    tokio::time::sleep(Duration::from_millis(300)).await;
                    continue;
                }
            };

        if reply.keys.is_empty() && (tick % 10 == 0) {
            if let Ok(rp) = conn
                .xread_options(&[cfg.tasks_stream.as_str()], &["0"], &opts_pending)
                .await
            {
                reply = rp;
            }
        }

        if reply.keys.is_empty() {
            tokio::time::sleep(Duration::from_millis(200)).await;
            continue;
        }

        for sk in reply.keys {
            for id in sk.ids {
                let msg_id = id.id.clone();

                let mut job_id = String::new();
                let mut payload = String::new();
                let mut extra_json: Option<String> = None;

                for (k, v) in id.map.iter() {
                    match k.as_str() {
                        "job_id" => {
                            job_id =
                                redis::from_redis_value::<String>(v.clone()).unwrap_or_default()
                        }
                        "payload" => {
                            payload =
                                redis::from_redis_value::<String>(v.clone()).unwrap_or_default()
                        }
                        "extra_json" => {
                            let s =
                                redis::from_redis_value::<String>(v.clone()).unwrap_or_default();
                            if !s.trim().is_empty() {
                                extra_json = Some(s);
                            }
                        }
                        _ => {}
                    }
                }

                if job_id.trim().is_empty() {
                    error!("[{consumer}] missing job_id, msg_id={msg_id}");
                    ack_del(&mut conn, &cfg.tasks_stream, &cfg.consumer_group, &msg_id).await;
                    continue;
                }

                let extra_val = extra_json
                    .as_deref()
                    .and_then(|s| serde_json::from_str::<JsonValue>(s).ok());

                let started = std::time::Instant::now();
                let result: Result<String, RuntimeError> =
                    state.llm.one_shot(&payload, extra_val).await;
                let elapsed_ms = started.elapsed().as_millis().to_string();

                match result {
                    Ok(text) => {
                        let _ = write_result(
                            &mut conn,
                            &cfg,
                            &job_id,
                            true,
                            Some(text),
                            None,
                            &elapsed_ms,
                        )
                        .await;

                        ack_del(&mut conn, &cfg.tasks_stream, &cfg.consumer_group, &msg_id).await;
                        info!("[{consumer}] done job_id={job_id} msg_id={msg_id}");
                    }
                    Err(e) => {
                        let _ = write_result(
                            &mut conn,
                            &cfg,
                            &job_id,
                            false,
                            None,
                            Some(e.to_string()),
                            &elapsed_ms,
                        )
                        .await;

                        ack_del(&mut conn, &cfg.tasks_stream, &cfg.consumer_group, &msg_id).await;
                        error!("[{consumer}] failed job_id={job_id}: {e}");
                    }
                }
            }
        }
    }
}

async fn ack_del(
    conn: &mut redis::aio::MultiplexedConnection,
    stream: &str,
    group: &str,
    msg_id: &str,
) {
    let _: redis::RedisResult<i64> = redis::cmd("XACK")
        .arg(stream)
        .arg(group)
        .arg(msg_id)
        .query_async::<i64>(conn)
        .await;

    let _: redis::RedisResult<i64> = redis::cmd("XDEL")
        .arg(stream)
        .arg(msg_id)
        .query_async::<i64>(conn)
        .await;
}

async fn write_result(
    conn: &mut redis::aio::MultiplexedConnection,
    cfg: &Settings,
    job_id: &str,
    ok: bool,
    output: Option<String>,
    err: Option<String>,
    elapsed_ms: &str,
) -> redis::RedisResult<String> {
    let mut cmd = redis::cmd("XADD");
    cmd.arg(&cfg.results_stream);

    if let Some(n) = cfg.result_stream_maxlen {
        cmd.arg("MAXLEN").arg("~").arg(n);
    }

    cmd.arg("*")
        .arg("job_id")
        .arg(job_id)
        .arg("ok")
        .arg(if ok { "true" } else { "false" })
        .arg("elapsed_ms")
        .arg(elapsed_ms);

    if let Some(out) = output {
        cmd.arg("output").arg(out);
    }
    if let Some(e) = err {
        cmd.arg("error").arg(e);
    }

    cmd.query_async::<String>(conn).await
}
