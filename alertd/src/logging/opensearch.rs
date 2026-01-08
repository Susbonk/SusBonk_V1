use anyhow::Result;
use reqwest::Client;
use serde_json::json;
use std::time::Duration;
use tokio_retry::strategy::{ExponentialBackoff, jitter};
use tokio_retry::Retry;
use tracing::{error, info, warn};
use crate::models::{LogEvent, SpamDetectionEvent, MonitoringEvent};

pub struct OpenSearchLogger {
    client: Client,
    base_url: String,
    index_prefix: String,
}

impl OpenSearchLogger {
    pub fn new(opensearch_url: String, index_prefix: String) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(10))
            .connect_timeout(Duration::from_secs(5))
            .build()
            .unwrap_or_else(|_| Client::new());

        Self {
            client,
            base_url: opensearch_url,
            index_prefix,
        }
    }

    async fn send_with_retry<F, Fut>(&self, operation: F) -> Result<()>
    where
        F: Fn() -> Fut,
        Fut: std::future::Future<Output = Result<reqwest::Response>>,
    {
        let retry_strategy = ExponentialBackoff::from_millis(100)
            .map(jitter)
            .take(3);

        Retry::spawn(retry_strategy, || async {
            match operation().await {
                Ok(response) => {
                    if response.status().is_success() {
                        Ok(())
                    } else {
                        warn!("OpenSearch request failed with status: {}", response.status());
                        Err(anyhow::anyhow!("Request failed: {}", response.status()))
                    }
                }
                Err(e) => {
                    warn!("OpenSearch request error: {}", e);
                    Err(e)
                }
            }
        })
        .await
    }

    pub async fn log_event(&self, event: &LogEvent) -> Result<()> {
        let index = format!("{}-logs-{}", self.index_prefix, event.timestamp.format("%Y-%m"));
        let url = format!("{}/{}/_doc", self.base_url, index);
        let event_json = serde_json::to_value(event)?;

        self.send_with_retry(|| {
            let client = self.client.clone();
            let url = url.clone();
            let event_json = event_json.clone();
            async move {
                client.post(&url).json(&event_json).send().await.map_err(Into::into)
            }
        })
        .await
    }

    pub async fn log_spam_detection(&self, event: &SpamDetectionEvent) -> Result<()> {
        let index = format!("{}-spam-{}", self.index_prefix, chrono::Utc::now().format("%Y-%m"));
        let url = format!("{}/{}/_doc", self.base_url, index);
        
        let log_entry = json!({
            "timestamp": chrono::Utc::now(),
            "event_type": "spam_detection",
            "data": event
        });

        self.send_with_retry(|| {
            let client = self.client.clone();
            let url = url.clone();
            let log_entry = log_entry.clone();
            async move {
                client.post(&url).json(&log_entry).send().await.map_err(Into::into)
            }
        })
        .await
    }

    pub async fn log_monitoring(&self, event: &MonitoringEvent) -> Result<()> {
        let index = format!("{}-metrics-{}", self.index_prefix, chrono::Utc::now().format("%Y-%m"));
        let url = format!("{}/{}/_doc", self.base_url, index);
        
        let log_entry = json!({
            "timestamp": chrono::Utc::now(),
            "event_type": "monitoring",
            "data": event
        });

        self.send_with_retry(|| {
            let client = self.client.clone();
            let url = url.clone();
            let log_entry = log_entry.clone();
            async move {
                client.post(&url).json(&log_entry).send().await.map_err(Into::into)
            }
        })
        .await
    }

    pub async fn create_index_templates(&self) -> Result<()> {
        let templates = vec![
            ("logs", self.get_logs_template()),
            ("spam", self.get_spam_template()),
            ("metrics", self.get_metrics_template()),
        ];

        for (name, template) in templates {
            let url = format!("{}/_index_template/{}-{}", self.base_url, self.index_prefix, name);
            
            match self.send_with_retry(|| {
                let client = self.client.clone();
                let url = url.clone();
                let template = template.clone();
                async move {
                    client.put(&url).json(&template).send().await.map_err(Into::into)
                }
            })
            .await
            {
                Ok(_) => info!("Created index template: {}-{}", self.index_prefix, name),
                Err(e) => error!("Failed to create index template {}-{}: {}", self.index_prefix, name, e),
            }
        }

        Ok(())
    }

    pub async fn health_check(&self) -> Result<()> {
        let url = format!("{}/_cluster/health", self.base_url);
        let response = self.client.get(&url).send().await?;
        
        if response.status().is_success() {
            Ok(())
        } else {
            Err(anyhow::anyhow!("Health check failed: {}", response.status()))
        }
    }

    fn get_logs_template(&self) -> serde_json::Value {
        json!({
            "index_patterns": [format!("{}-logs-*", self.index_prefix)],
            "template": {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "service": {"type": "keyword"},
                        "message": {"type": "text"},
                        "metadata": {"type": "object"}
                    }
                }
            }
        })
    }

    fn get_spam_template(&self) -> serde_json::Value {
        json!({
            "index_patterns": [format!("{}-spam-*", self.index_prefix)],
            "template": {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "event_type": {"type": "keyword"},
                        "data.message_id": {"type": "keyword"},
                        "data.chat_id": {"type": "keyword"},
                        "data.spam_score": {"type": "float"},
                        "data.blocked": {"type": "boolean"}
                    }
                }
            }
        })
    }

    fn get_metrics_template(&self) -> serde_json::Value {
        json!({
            "index_patterns": [format!("{}-metrics-*", self.index_prefix)],
            "template": {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "event_type": {"type": "keyword"},
                        "data.metric_name": {"type": "keyword"},
                        "data.value": {"type": "float"},
                        "data.unit": {"type": "keyword"}
                    }
                }
            }
        })
    }
}
