use reqwest::Client;
use serde::Deserialize;
use serde_json::json;
use tracing::warn;
use crate::LogEvent;

#[derive(Debug, Deserialize)]
struct BulkResponse {
    errors: bool,
    items: Vec<BulkItem>,
}

#[derive(Debug, Deserialize)]
struct BulkItem {
    index: Option<BulkItemResult>,
}

#[derive(Debug, Deserialize)]
struct BulkItemResult {
    status: u16,
    error: Option<BulkError>,
}

#[derive(Debug, Deserialize)]
struct BulkError {
    #[serde(rename = "type")]
    error_type: String,
    reason: String,
}

pub struct OpenSearchClient {
    client: Client,
    base_url: String,
}

impl OpenSearchClient {
    pub fn new(base_url: String) -> Self {
        Self {
            client: crate::http::create_client(),
            base_url,
        }
    }

    pub fn base_url(&self) -> &str {
        &self.base_url
    }

    pub async fn bulk_index(&self, events: Vec<LogEvent>) -> anyhow::Result<usize> {
        let bulk_body = to_bulk_ndjson(&events)?;

        let response = self.client
            .post(&format!("{}/_bulk", self.base_url))
            .header("Content-Type", "application/x-ndjson")
            .body(bulk_body)
            .send()
            .await?;

        if !response.status().is_success() {
            return Err(anyhow::anyhow!("Bulk index failed: {}", response.status()));
        }

        let result: BulkResponse = response.json().await?;
        
        if result.errors {
            let mut failed = 0;
            for item in &result.items {
                if let Some(idx) = &item.index {
                    if idx.status >= 400 {
                        failed += 1;
                        if let Some(err) = &idx.error {
                            warn!("Bulk index error: {} - {}", err.error_type, err.reason);
                        }
                    }
                }
            }
            if failed > 0 {
                return Err(anyhow::anyhow!("{} of {} documents failed to index", failed, events.len()));
            }
        }

        Ok(events.len())
    }

    pub async fn search(&self, index: &str, query: serde_json::Value) -> anyhow::Result<serde_json::Value> {
        let response = self.client
            .post(&format!("{}/{}/_search", self.base_url, index))
            .json(&query)
            .send()
            .await?;

        Ok(response.json().await?)
    }

    pub async fn get_nodes_stats_fs(&self) -> anyhow::Result<serde_json::Value> {
        let response = self.client
            .get(&format!("{}/_nodes/stats/fs", self.base_url))
            .send()
            .await?;

        Ok(response.json().await?)
    }
}

pub fn to_bulk_ndjson(events: &[LogEvent]) -> anyhow::Result<String> {
    let mut bulk_body = String::new();
    
    for event in events {
        let timestamp = event.timestamp.unwrap_or_else(chrono::Utc::now);
        let service_name = event.service_name_or_default();
        let index = format!("logs-{}-{}", service_name, timestamp.format("%Y.%m.%d"));
        
        let action = json!({"index": {"_index": index}});
        bulk_body.push_str(&serde_json::to_string(&action)?);
        bulk_body.push('\n');
        bulk_body.push_str(&serde_json::to_string(&event)?);
        bulk_body.push('\n');
    }

    Ok(bulk_body)
}

