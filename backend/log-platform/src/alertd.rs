use std::sync::Arc;
use std::time::Duration;
use tracing::{info, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use reqwest::Client;
use serde_json::json;

use log_platform::{LogEvent, Service, LogMeta};

struct AlertEngine {
    client: Client,
    ingest_url: String,
    opensearch_url: String,
}

impl AlertEngine {
    fn new(ingest_url: String, opensearch_url: String) -> Self {
        Self {
            client: Client::new(),
            ingest_url,
            opensearch_url,
        }
    }

    async fn log_spam_detection(&self, message_id: &str, spam_score: f64, blocked: bool) -> anyhow::Result<()> {
        let event = LogEvent {
            timestamp: Some(chrono::Utc::now()),
            service: Some(Service { name: "alertd".to_string() }),
            log: Some(LogMeta { level: Some("info".to_string()) }),
            message: Some(format!("Spam detected: score={}, blocked={}", spam_score, blocked)),
            trace: None,
            labels: None,
            fields: Some(json!({
                "message_id": message_id,
                "spam_score": spam_score,
                "blocked": blocked,
                "event_type": "spam_detection"
            })),
        };

        self.client
            .post(&format!("{}/ingest", self.ingest_url))
            .json(&event)
            .send()
            .await?;

        Ok(())
    }

    async fn log_metric(&self, metric_name: &str, value: f64) -> anyhow::Result<()> {
        let event = LogEvent {
            timestamp: Some(chrono::Utc::now()),
            service: Some(Service { name: "alertd".to_string() }),
            log: Some(LogMeta { level: Some("info".to_string()) }),
            message: Some(format!("Metric: {}={}", metric_name, value)),
            trace: None,
            labels: None,
            fields: Some(json!({
                "metric_name": metric_name,
                "value": value,
                "event_type": "metric"
            })),
        };

        self.client
            .post(&format!("{}/ingest", self.ingest_url))
            .json(&event)
            .send()
            .await?;

        Ok(())
    }

    async fn check_for_errors(&self) -> anyhow::Result<usize> {
        let query = json!({
            "query": {
                "bool": {
                    "must": [
                        { "match": { "log.level": "error" }},
                        { "range": { "@timestamp": { "gte": "now-5m" }}}
                    ]
                }
            },
            "size": 0
        });

        let response = self.client
            .post(&format!("{}/logs-*/_search", self.opensearch_url))
            .json(&query)
            .send()
            .await?;

        let result: serde_json::Value = response.json().await?;
        let error_count = result["hits"]["total"]["value"].as_u64().unwrap_or(0) as usize;

        Ok(error_count)
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

    let opensearch_url = std::env::var("OPENSEARCH_URL")
        .unwrap_or_else(|_| "http://localhost:9200".to_string());
    let ingest_url = std::env::var("INGEST_URL")
        .unwrap_or_else(|_| "http://localhost:8080".to_string());

    let engine = Arc::new(AlertEngine::new(ingest_url, opensearch_url));

    // Example: Log spam detection
    engine.log_spam_detection("msg_123", 0.95, true).await?;
    
    // Example: Log metric
    engine.log_metric("messages_processed", 1.0).await?;

    info!("alertd service running. Press Ctrl+C to stop.");

    // Monitoring loop
    let engine_clone = engine.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(Duration::from_secs(60));
        loop {
            interval.tick().await;
            match engine_clone.check_for_errors().await {
                Ok(count) if count > 0 => {
                    info!("Found {} errors in last 5 minutes", count);
                }
                Err(e) => error!("Failed to check for errors: {}", e),
                _ => {}
            }
        }
    });
    
    tokio::signal::ctrl_c().await?;
    info!("Shutting down alertd service");

    Ok(())
}
