use reqwest::Client;
use serde_json::Value;
use serde_json::json;
use std::time::Duration;

use tracing::{info, warn};

use log_platform_common::env;
use log_platform_common::notify::{EmailNotifier, MultiNotifier, Notifier, StdoutNotifier};
use log_platform_domain::Alert;

//
// -------------------- config --------------------
//

#[derive(Clone)]
struct Cfg {
    os_url: String,
    interval: Duration,
    min_free_gb: f64,
    min_free_pct: f64,
    index_pattern: String,
    error_threshold: u32,
    warning_threshold: u32,
    details_limit: usize,
}

impl Cfg {
    fn from_env() -> Self {
        Self {
            os_url: env::env_string("OPENSEARCH_URL", "http://localhost:9200"),
            interval: env::env_duration_secs("ALERT_INTERVAL_SEC", 60),
            min_free_gb: env::env_parse("MIN_FREE_GB", 15.0f64),
            min_free_pct: env::env_parse("MIN_FREE_PCT", 12.0f64),
            index_pattern: env::env_string("LOG_INDEX_PATTERN", "logs-*"),
            error_threshold: env::env_parse("ERROR_THRESHOLD", 1u32),
            warning_threshold: env::env_parse("WARNING_THRESHOLD", 5u32),
            details_limit: env::env_parse("ALERT_DETAILS_LIMIT", 5usize),
        }
    }
}

//
// -------------------- http helpers --------------------
//

async fn get_json(http: &Client, url: &str) -> anyhow::Result<Value> {
    let r = http.get(url).send().await?;
    let status = r.status();
    let text = r.text().await.unwrap_or_default();

    if !status.is_success() {
        anyhow::bail!("{} -> {} {}", url, status, text);
    }

    Ok(serde_json::from_str(&text)?)
}

async fn post_json(http: &Client, url: &str, body: Value) -> anyhow::Result<Value> {
    let r = http
        .post(url)
        .header("Content-Type", "application/json")
        .json(&body)
        .send()
        .await?;

    let status = r.status();
    if !status.is_success() {
        anyhow::bail!(
            "{} -> {} {}",
            url,
            status,
            r.text().await.unwrap_or_default()
        );
    }

    match r.json::<Value>().await {
        Ok(json) => Ok(json),
        Err(e) => anyhow::bail!("JSON parse error: {e}"),
    }
}

//
// -------------------- checks --------------------
//

async fn check_disk(cfg: &Cfg, http: &Client, n: &dyn Notifier) {
    let url = format!("{}/_nodes/stats/fs", cfg.os_url.trim_end_matches('/'));

    let v = match get_json(http, &url).await {
        Ok(v) => v,
        Err(e) => {
            n.notify(Alert {
                severity: "WARN".to_string(),
                kind: "CHECK_FAILED".to_string(),
                message: format!("disk check error: {e}"),
            });
            return;
        }
    };

    let Some(nodes) = v.get("nodes").and_then(|x| x.as_object()) else {
        n.notify(Alert {
            severity: "WARN".to_string(),
            kind: "CHECK_FAILED".to_string(),
            message: "unexpected nodes stats shape".into(),
        });
        return;
    };

    for (_id, node) in nodes {
        let name = node
            .get("name")
            .and_then(|x| x.as_str())
            .unwrap_or("unknown");

        let total = node
            .get("fs")
            .and_then(|x| x.get("total"))
            .and_then(|x| x.as_object());

        let (avail_b, total_b) = match total {
            Some(t) => (
                t.get("available_in_bytes")
                    .and_then(|x| x.as_f64())
                    .unwrap_or(0.0),
                t.get("total_in_bytes")
                    .and_then(|x| x.as_f64())
                    .unwrap_or(1.0),
            ),
            None => (0.0, 1.0),
        };

        let free_gb = log_platform_common::parse::bytes_to_gb(avail_b);
        let free_pct = (avail_b / total_b) * 100.0;

        if free_gb < cfg.min_free_gb || free_pct < cfg.min_free_pct {
            n.notify(Alert {
                severity: "CRIT".to_string(),
                kind: "DISK".to_string(),
                message: format!(
                    "node={name} free={free_gb:.1}GB ({free_pct:.1}%) thresholds: <{:.1}GB or <{:.1}%",
                    cfg.min_free_gb, cfg.min_free_pct
                ),
            });
        }
    }
}

async fn check_readonly(cfg: &Cfg, http: &Client, n: &dyn Notifier) {
    let url = format!(
        "{}/{}/_settings/index.blocks.read_only_allow_delete",
        cfg.os_url.trim_end_matches('/'),
        cfg.index_pattern
    );

    let v = match get_json(http, &url).await {
        Ok(v) => v,
        Err(e) => {
            n.notify(Alert {
                severity: "WARN".to_string(),
                kind: "CHECK_FAILED".to_string(),
                message: format!("readonly check error: {e}"),
            });
            return;
        }
    };

    let Some(obj) = v.as_object() else { return };

    for (index, payload) in obj {
        let ro = payload
            .get("settings")
            .and_then(|x| x.get("index"))
            .and_then(|x| x.get("blocks"))
            .and_then(|x| x.get("read_only_allow_delete"));

        if matches!(ro, Some(Value::Bool(true)))
            || matches!(ro, Some(Value::String(s)) if s == "true")
        {
            n.notify(Alert {
                severity: "CRIT".to_string(),
                kind: "READONLY".to_string(),
                message: format!("index={index} has read_only_allow_delete=true"),
            });
        }
    }
}

fn extract_messages(hits: &[Value], limit: usize) -> Vec<String> {
    hits.iter()
        .take(limit)
        .enumerate()
        .map(|(i, hit)| {
            let src = hit.get("_source").unwrap_or(&Value::Null);

            let ts = src
                .get("@timestamp")
                .and_then(|v| v.as_str())
                .unwrap_or("?");

            let level = src
                .get("log")
                .and_then(|v| v.get("level"))
                .and_then(|v| v.as_str())
                .or_else(|| src.get("log.level").and_then(|v| v.as_str()))
                .unwrap_or("?");

            let service = src
                .get("service")
                .and_then(|v| v.get("name"))
                .and_then(|v| v.as_str())
                .or_else(|| src.get("service.name").and_then(|v| v.as_str()))
                .unwrap_or("?");

            let msg = src
                .get("message")
                .and_then(|v| v.as_str())
                .unwrap_or("No message available");

            format!("{:02}. {} [{}] {} — {}", i + 1, ts, level, service, msg)
        })
        .collect()
}

async fn check_log_warnings_errors(cfg: &Cfg, http: &Client, n: &dyn Notifier) {
    let url = format!(
        "{}/{}/_search",
        cfg.os_url.trim_end_matches('/'),
        cfg.index_pattern
    );

    let level_field = "log.level";

    // ---------- ERRORS / CRITICAL / FATAL ----------
    let error_query = json!({
        "query": {
            "bool": {
                "filter": [
                    { "range": { "@timestamp": { "gte": "now-3m" } } },
                    { "terms": { level_field: ["ERROR", "CRITICAL", "FATAL"] } }
                ]
            }
        },
        "sort": [{ "@timestamp": { "order": "desc" } }],
        "size": 10
    });

    let error_v = match post_json(http, &url, error_query).await {
        Ok(json) => json,
        Err(e) => {
            n.notify(Alert {
                severity: "WARN".to_string(),
                kind: "CHECK_FAILED".to_string(),
                message: format!("log error check request error: {e}"),
            });
            return;
        }
    };

    let empty_hits = vec![];
    let error_hits = error_v
        .get("hits")
        .and_then(|h| h.get("hits"))
        .and_then(|h| h.as_array())
        .unwrap_or(&empty_hits);

    if !error_hits.is_empty() {
        let error_count = error_hits.len();
        if error_count >= cfg.error_threshold as usize {
            let details = extract_messages(error_hits, cfg.details_limit).join("\n");
            n.notify(Alert {
                severity: "CRIT".to_string(),
                kind: "LOG_ERROR".to_string(),
                message: format!(
                    "Found {} error(s) in logs (threshold: {}). Recent:\n{}",
                    error_count, cfg.error_threshold, details
                ),
            });
        }
    }

    // ---------- WARNINGS ----------
    let warning_query = json!({
        "query": {
            "bool": {
                "filter": [
                    { "range": { "@timestamp": { "gte": "now-3m" } } },
                    { "terms": { level_field: ["WARN", "WARNING"] } }
                ]
            }
        },
        "sort": [{ "@timestamp": { "order": "desc" } }],
        "size": 10
    });

    let warning_v = match post_json(http, &url, warning_query).await {
        Ok(json) => json,
        Err(e) => {
            n.notify(Alert {
                severity: "WARN".to_string(),
                kind: "CHECK_FAILED".to_string(),
                message: format!("log warning check request error: {e}"),
            });
            return;
        }
    };

    let empty_warning_hits = vec![];
    let warning_hits = warning_v
        .get("hits")
        .and_then(|h| h.get("hits"))
        .and_then(|h| h.as_array())
        .unwrap_or(&empty_warning_hits);

    if !warning_hits.is_empty() {
        let warning_count = warning_hits.len();
        if warning_count >= cfg.warning_threshold as usize {
            let details = extract_messages(warning_hits, cfg.details_limit).join("\n");
            n.notify(Alert {
                severity: "WARN".to_string(),
                kind: "LOG_WARNING".to_string(),
                message: format!(
                    "Found {} warning(s) in logs (threshold: {}). Recent:\n{}",
                    warning_count, cfg.warning_threshold, details
                ),
            });
        }
    }
}

//
// -------------------- main --------------------
//

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO) // Use INFO as default, but can be overridden by RUST_LOG
        .with_target(false)
        .init();

    let cfg = Cfg::from_env();
    let http = log_platform_common::http::client(Duration::from_secs(5));

    let mut sinks: Vec<Box<dyn Notifier>> = vec![Box::new(StdoutNotifier)];

    if let Ok(email_notifier) = EmailNotifier::from_env() {
        info!(
            "email notifications enabled: server={} port={} user={}",
            email_notifier.cfg.smtp_server,
            email_notifier.cfg.smtp_port,
            email_notifier.cfg.smtp_user,
        );
        sinks.push(Box::new(email_notifier));
    } else {
        warn!("EMAIL_ENABLED=1 but SMTP/EMAIL env vars are incomplete");
    }

    let notifier = MultiNotifier::new(sinks);

    tracing::info!("alertd started, interval={}s", cfg.interval.as_secs());

    loop {
        check_disk(&cfg, &http, &notifier).await;
        check_readonly(&cfg, &http, &notifier).await;
        check_log_warnings_errors(&cfg, &http, &notifier).await;
        tokio::time::sleep(cfg.interval).await;
    }
}
