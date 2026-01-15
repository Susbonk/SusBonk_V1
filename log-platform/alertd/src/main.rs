use std::sync::Arc;
use std::time::Duration;
use tracing::{info, error, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use reqwest::Client;
use serde_json::json;

use log_platform_common::{
    LogEvent, Service, LogMeta, AlertLevel,
    env::Cfg,
    opensearch::OpenSearchClient,
    notify::{MultiNotifier, LogNotifier, EmailNotifier},
};

struct AlertEngine {
    client: Client,
    cfg: Cfg,
    opensearch: OpenSearchClient,
    notifier: MultiNotifier,
}

impl AlertEngine {
    fn new(cfg: Cfg) -> Self {
        let notifier = MultiNotifier::new()
            .add(Box::new(LogNotifier))
            .add(Box::new(EmailNotifier::new(
                cfg.smtp_host.clone(),
                cfg.smtp_port,
                cfg.alert_email_from.clone(),
                cfg.alert_email_to.clone(),
                cfg.smtp_user.clone(),
                cfg.smtp_password.clone(),
            )));

        Self {
            client: log_platform_common::http::create_client(),
            opensearch: OpenSearchClient::new(cfg.opensearch_url.clone()),
            cfg,
            notifier,
        }
    }

    async fn log_event(&self, level: &str, message: String, fields: serde_json::Value) -> anyhow::Result<()> {
        let event = LogEvent {
            timestamp: Some(chrono::Utc::now()),
            service: Some(Service { name: "alertd".to_string() }),
            log: Some(LogMeta { level: Some(level.to_string()) }),
            message: Some(message),
            trace: None,
            labels: None,
            fields: Some(fields),
        };

        self.client
            .post(&format!("{}/ingest", self.cfg.ingest_url))
            .json(&event)
            .send()
            .await?;

        Ok(())
    }

    async fn check_disk(&self) -> anyhow::Result<()> {
        let stats = self.opensearch.get_nodes_stats_fs().await?;
        
        if let Some(nodes) = stats["nodes"].as_object() {
            for (node_id, node_data) in nodes {
                let total = node_data["fs"]["total"]["total_in_bytes"].as_f64().unwrap_or(0.0);
                let free = node_data["fs"]["total"]["free_in_bytes"].as_f64().unwrap_or(0.0);
                let used_gb = (total - free) / 1_073_741_824.0;
                let used_pct = if total > 0.0 { ((total - free) / total) * 100.0 } else { 0.0 };

                info!("Node {}: {:.2} GB used ({:.1}%)", node_id, used_gb, used_pct);

                if used_gb > self.cfg.disk_threshold_gb {
                    let msg = format!("Node {} disk usage: {:.2} GB ({:.1}%)", node_id, used_gb, used_pct);
                    self.notifier.send_simple("Disk Alert", &msg, AlertLevel::Warning).await;
                    self.log_event("warn", msg, json!({
                        "node_id": node_id,
                        "disk_gb": used_gb,
                        "disk_pct": used_pct,
                        "event_type": "disk_alert"
                    })).await?;
                }
            }
        }

        Ok(())
    }

    async fn check_readonly(&self) -> anyhow::Result<()> {
        let response = self.client
            .get(&format!("{}/logs-*/_settings", self.opensearch.base_url()))
            .send()
            .await?;

        let settings: serde_json::Value = response.json().await?;
        
        for (index, data) in settings.as_object().unwrap_or(&serde_json::Map::new()) {
            if let Some(readonly) = data["settings"]["index"]["blocks"]["read_only_allow_delete"].as_str() {
                if readonly == "true" {
                    let msg = format!("Index {} is read-only", index);
                    warn!("{}", msg);
                    self.notifier.send_simple("Read-Only Alert", &msg, AlertLevel::Error).await;
                    self.log_event("error", msg, json!({"index": index, "event_type": "readonly_alert"})).await?;
                }
            }
        }

        Ok(())
    }

    async fn check_log_warnings_errors(&self) -> anyhow::Result<()> {
        let query = json!({
            "query": {
                "bool": {
                    "must": [
                        {"terms": {"log.level": ["warn", "error"]}},
                        {"range": {"@timestamp": {"gte": "now-5m"}}}
                    ]
                }
            },
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "log.level"}
                }
            }
        });

        let result = self.opensearch.search("logs-*", query).await?;
        
        if let Some(buckets) = result["aggregations"]["by_level"]["buckets"].as_array() {
            for bucket in buckets {
                let level = bucket["key"].as_str().unwrap_or("");
                let count = bucket["doc_count"].as_u64().unwrap_or(0) as usize;

                let threshold = match level {
                    "warn" => self.cfg.warn_threshold,
                    "error" => self.cfg.error_threshold,
                    _ => continue,
                };

                if count > threshold {
                    let msg = format!("{} {}s in last 5 minutes (threshold: {})", count, level, threshold);
                    warn!("{}", msg);
                    self.notifier.send_simple(
                        &format!("{} Alert", level.to_uppercase()),
                        &msg,
                        AlertLevel::Warning
                    ).await;
                    self.log_event("warn", msg, json!({
                        "level": level,
                        "count": count,
                        "threshold": threshold,
                        "event_type": "log_threshold_alert"
                    })).await?;
                }
            }
        }

        Ok(())
    }

    async fn log_spam_detection(&self, message_id: &str, spam_score: f64, blocked: bool) -> anyhow::Result<()> {
        self.log_event(
            "info",
            format!("Spam detected: score={}, blocked={}", spam_score, blocked),
            json!({
                "message_id": message_id,
                "spam_score": spam_score,
                "blocked": blocked,
                "event_type": "spam_detection"
            })
        ).await
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "alertd=debug,info".into()),
        )
        .with(tracing_subscriber::fmt::layer().json())
        .init();

    info!("Starting alertd service");

    let cfg = Cfg::from_env();
    info!("Config: disk_threshold={}GB, warn_threshold={}, error_threshold={}, interval={}s",
          cfg.disk_threshold_gb, cfg.warn_threshold, cfg.error_threshold, cfg.check_interval_secs);

    let engine = Arc::new(AlertEngine::new(cfg.clone()));

    // Example: Log spam detection
    engine.log_spam_detection("msg_123", 0.95, true).await?;

    info!("alertd service running. Press Ctrl+C to stop.");

    // Monitoring loop
    let engine_clone = engine.clone();
    let interval_secs = cfg.check_interval_secs;
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(Duration::from_secs(interval_secs));
        loop {
            interval.tick().await;
            
            if let Err(e) = engine_clone.check_disk().await {
                error!("Disk check failed: {}", e);
            }
            
            if let Err(e) = engine_clone.check_readonly().await {
                error!("Read-only check failed: {}", e);
            }
            
            if let Err(e) = engine_clone.check_log_warnings_errors().await {
                error!("Log threshold check failed: {}", e);
            }
        }
    });
    
    tokio::signal::ctrl_c().await?;
    info!("Shutting down alertd service");

    Ok(())
}
