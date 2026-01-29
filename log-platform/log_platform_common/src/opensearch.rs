use anyhow::Result;
use chrono::{DateTime, Utc};
use reqwest::Client;
use serde_json::json;

use log_platform_domain::LogEvent;

pub fn index_name(service: &str, ts: DateTime<Utc>) -> String {
    let index = format!("logs-{}-{}", service, ts.format("%Y.%m.%d"));
    tracing::trace!(
        "computed index name: {} for service {} at {}",
        index,
        service,
        ts
    );
    index
}

pub fn to_bulk_ndjson(events: &[LogEvent]) -> Result<(String, usize)> {
    let mut out = String::new();
    for ev in events {
        let ts = ev.timestamp.unwrap_or_else(Utc::now);
        let service = ev.service_name_or_default();
        let idx = index_name(&service, ts);

        // action line
        out.push_str(&serde_json::to_string(&json!({"index": {"_index": idx}}))?);
        out.push('\n');

        // source line
        out.push_str(&serde_json::to_string(ev)?);
        out.push('\n');
    }
    tracing::debug!("converted {} events to bulk NDJSON format", events.len());
    Ok((out, events.len()))
}

/// A wrapper struct to encapsulate OpenSearch operations
pub struct OpenSearch {
    pub base_url: String,
    pub http: Client,
}

impl OpenSearch {
    pub fn new(base_url: String, http: Client) -> Self {
        Self { base_url, http }
    }

    pub async fn bulk_ingest(&self, events: &[LogEvent]) -> Result<usize> {
        let (body, count) = to_bulk_ndjson(events)?;
        let url = format!("{}/_bulk", self.base_url.trim_end_matches('/'));

        let resp = self
            .http
            .post(&url)
            .header("Content-Type", "application/x-ndjson")
            .body(body)
            .send()
            .await?;

        let status = resp.status();
        let text = resp.text().await.unwrap_or_default();

        if !status.is_success() {
            anyhow::bail!("opensearch bulk request failed: {} - {}", status, text);
        }

        let v: serde_json::Value = serde_json::from_str(&text)?;
        if v.get("errors").and_then(|x| x.as_bool()) == Some(true) {
            anyhow::bail!("opensearch bulk returned errors: {}", v);
        }

        Ok(count)
    }

    pub async fn search(
        &self,
        index_pattern: &str,
        query: &serde_json::Value,
    ) -> Result<serde_json::Value> {
        let url = format!(
            "{}/{}/_search",
            self.base_url.trim_end_matches('/'),
            index_pattern
        );

        let resp = self
            .http
            .post(&url)
            .header("Content-Type", "application/json")
            .json(query)
            .send()
            .await?;

        let status = resp.status();
        if !status.is_success() {
            anyhow::bail!("opensearch search request failed: {}", status);
        }

        let response: serde_json::Value = resp.json().await?;
        Ok(response)
    }
}
