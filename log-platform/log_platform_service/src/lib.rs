use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;

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

    // Free form fields
    #[serde(default)]
    pub labels: Option<Value>,

    #[serde(default)]
    pub fields: Option<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Service {
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogMeta {
    pub level: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trace {
    pub id: Option<String>,
}

impl LogEvent {
    pub fn service_name_or_default(&self) -> String {
        self.service
            .as_ref()
            .map(|s| s.name.clone())
            .unwrap_or_else(|| "app".to_string())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Alert {
    pub severity: String,
    pub kind: String,
    pub message: String,
}
