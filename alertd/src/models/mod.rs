use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEvent {
    pub id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub level: LogLevel,
    pub service: String,
    pub message: String,
    pub metadata: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum LogLevel {
    Error,
    Warn,
    Info,
    Debug,
    Trace,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpamDetectionEvent {
    pub message_id: String,
    pub chat_id: String,
    pub user_id: String,
    pub content: String,
    pub spam_score: f64,
    pub blocked: bool,
    pub detection_rules: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringEvent {
    pub metric_name: String,
    pub value: f64,
    pub unit: String,
    pub tags: std::collections::HashMap<String, String>,
}
