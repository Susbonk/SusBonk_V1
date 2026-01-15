use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use serde_json::Value;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Service {
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogMeta {
    #[serde(default)]
    pub level: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trace {
    #[serde(default)]
    pub id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEvent {
    #[serde(rename = "@timestamp", default)]
    pub timestamp: Option<DateTime<Utc>>,
    #[serde(default)]
    pub service: Option<Service>,
    #[serde(default)]
    pub log: Option<LogMeta>,
    #[serde(default)]
    pub message: Option<String>,
    #[serde(default)]
    pub trace: Option<Trace>,
    #[serde(default)]
    pub labels: Option<Value>,
    #[serde(default)]
    pub fields: Option<Value>,
}

impl LogEvent {
    pub fn service_name_or_default(&self) -> &str {
        self.service.as_ref().map(|s| s.name.as_str()).unwrap_or("unknown")
    }
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
pub enum IngestPayload {
    Single(LogEvent),
    Batch(Vec<LogEvent>),
}

impl IngestPayload {
    pub fn into_vec(self) -> Vec<LogEvent> {
        match self {
            IngestPayload::Single(event) => vec![event],
            IngestPayload::Batch(events) => events,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct IngestResponse {
    pub indexed: usize,
}
