use std::net::SocketAddr;

use anyhow::Result;
use teloxide::{error_handlers::LoggingErrorHandler, prelude::*, update_listeners::webhooks};
use tracing::info;
use tracing_subscriber::prelude::*;

use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::sync::mpsc;
use tokio::task::JoinSet;

mod bot;
mod opensearch_ingest;
mod database;
mod services;
mod redis_service;
mod ai_models;

mod workers;

use config::{CONFIG, RunMode};

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();

    // Best-effort bridge: log -> tracing (do not panic if already set)
    let _ = tracing_log::LogTracer::init();

    // RUST_LOG overrides CONFIG.log_level
    let filter = if let Ok(env) = std::env::var("RUST_LOG") {
        tracing_subscriber::EnvFilter::new(env)
    } else {
        tracing_subscriber::EnvFilter::new(CONFIG.log_level.clone())
    };

    // Optional OpenSearch ingest
    let ingest_url = std::env::var("OS_INGEST_URL")
        .ok()
        .filter(|v| !v.trim().is_empty());

    let os_handle = if let Some(url) = ingest_url {
        let (layer, handle) =
            opensearch_ingest::opensearch_ingest_layer(opensearch_ingest::OpenSearchIngestConfig {
                ingest_url: url,
                service_name: "telegram-bot".to_string(),
                ..Default::default()
            });

        // IMPORTANT: use try_init() + ignore Result to avoid panic on double-init
        let _ = tracing_subscriber::registry()
            .with(tracing_subscriber::fmt::layer())
            .with(filter)
            .with(layer)
            .try_init();

        Some(handle)
    } else {
        let _ = tracing_subscriber::registry()
            .with(tracing_subscriber::fmt::layer())
            .with(filter)
            .try_init();

        None
    };

    CONFIG.log_effective();
    info!("starting bot…");

    // Connect to database
    let db = database::connect().await?;
    info!("database connected");

    let bot = Bot::from_env();

    info!("clearing pending updates…");
    bot.delete_webhook().drop_pending_updates(true).await?;

    let (group_tx, group_rx) = mpsc::channel::<bot::handlers::GroupWorkItem>(10_000);

    // Receiver is shared between workers via Mutex
    let group_rx = Arc::new(Mutex::new(group_rx));

    let mut worker_set = JoinSet::new();

    let workers = std::env::var("GROUP_WORKERS")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .unwrap_or(4);

    // Spawn group workers using the dedicated module
    for i in 0..workers {
        let bot_clone = bot.clone();
        let rx_clone = group_rx.clone();
        let db_clone = db.clone();
        let worker_id = i + 1;

        worker_set.spawn(async move {
            crate::workers::group_worker::run_group_worker(worker_id, bot_clone, rx_clone, db_clone).await;
        });
    }

    let handler = bot::make_handler();

    match CONFIG.run_mode {
        RunMode::Polling => {
            info!("running in POLLING mode");
            Dispatcher::builder(bot, handler)
                .dependencies(dptree::deps![group_tx.clone(), db.clone()])
                .enable_ctrlc_handler()
                .build()
                .dispatch()
                .await;
        }
        RunMode::Webhook => {
            info!("running in WEBHOOK mode");

            let port = CONFIG
                .port
                .expect("validated: port must exist in webhook mode");
            let addr: SocketAddr = ([0, 0, 0, 0], port).into();

            let public_url: url::Url = CONFIG
                .webhook_url
                .as_deref()
                .expect("validated: webhook_url must exist in webhook mode")
                .parse()
                .expect("WEBHOOK_URL must be valid URL");

            let listener = webhooks::axum(bot.clone(), webhooks::Options::new(addr, public_url))
                .await
                .expect("couldn't setup webhook");

            Dispatcher::builder(bot, handler)
                .dependencies(dptree::deps![group_tx.clone(), db.clone()])
                .enable_ctrlc_handler()
                .build()
                .dispatch_with_listener(listener, LoggingErrorHandler::new())
                .await;
        }
    }

    // Shutdown sequence:
    drop(group_tx); // Close the channel

    while let Some(res) = worker_set.join_next().await {
        if let Err(e) = res {
            tracing::error!("group worker join error: {e}");
        }
    }

    // Graceful flush on shutdown (best-effort)
    if let Some(h) = os_handle {
        h.shutdown().await;
    }

    Ok(())
}
