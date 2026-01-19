use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

// Spam detection types for Redis Streams
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DetectionType {
    SuspiciousLink,
    ShortenedUrl,
    UnknownDomain,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserInfo {
    pub id: i64,
    pub username: Option<String>,
    pub first_name: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpamEvent {
    pub timestamp: DateTime<Utc>,
    pub chat_id: i64,
    pub user: UserInfo,
    pub detection_type: DetectionType,
    pub message_text: String,
    pub detected_content: String,
    pub confidence: f32,
}

// Log platform types
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
    pub trace: Option<serde_json::Value>,
    #[serde(default)]
    pub labels: Option<serde_json::Value>,
    #[serde(default)]
    pub fields: Option<serde_json::Value>,
}
