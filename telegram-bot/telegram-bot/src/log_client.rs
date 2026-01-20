use crate::types::{LogEvent, Service, LogMeta};
use reqwest::Client;
use chrono::Utc;
use tracing::{info, error};
use serde_json::json;

pub struct LogPlatformClient {
    client: Client,
    ingest_url: String,
}

impl LogPlatformClient {
    pub fn new(ingest_url: String) -> Self {
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(30))
            .build()
            .unwrap_or_else(|_| Client::new());
        
        Self {
            client,
            ingest_url,
        }
    }

    pub async fn log_bot_event(&self, level: &str, message: &str, labels: Option<serde_json::Value>) {
        let log_event = LogEvent {
            timestamp: Some(Utc::now()),
            service: Some(Service {
                name: "telegram-bot".to_string(),
            }),
            log: Some(LogMeta {
                level: Some(level.to_string()),
            }),
            message: Some(message.to_string()),
            trace: None,
            labels,
            fields: None,
        };

        if let Err(e) = self.send_log_event(log_event).await {
            error!("Failed to send log event to log platform: {}", e);
        }
    }

    pub async fn log_startup(&self) {
        self.log_bot_event(
            "info",
            "Telegram bot started successfully",
            Some(json!({
                "event_type": "startup",
                "component": "telegram-bot"
            }))
        ).await;
    }

    #[allow(dead_code)]
    pub async fn log_shutdown(&self) {
        self.log_bot_event(
            "info",
            "Telegram bot shutting down",
            Some(json!({
                "event_type": "shutdown",
                "component": "telegram-bot"
            }))
        ).await;
    }

    pub async fn log_spam_detection(&self, chat_id: i64, detection_type: &str, confidence: f32) {
        self.log_bot_event(
            "info",
            &format!("Spam detected in chat {}", chat_id),
            Some(json!({
                "event_type": "spam_detection",
                "chat_id": chat_id,
                "detection_type": detection_type,
                "confidence": confidence
            }))
        ).await;
    }

    pub async fn log_command_execution(&self, chat_id: i64, command: &str, user_id: i64, success: bool) {
        let level = if success { "info" } else { "warn" };
        let message = format!("Command {} executed by user {} in chat {}", command, user_id, chat_id);
        
        self.log_bot_event(
            level,
            &message,
            Some(json!({
                "event_type": "command_execution",
                "chat_id": chat_id,
                "command": command,
                "user_id": user_id,
                "success": success
            }))
        ).await;
    }

    pub async fn log_error(&self, error_message: &str, context: Option<serde_json::Value>) {
        let mut labels = json!({
            "event_type": "error",
            "component": "telegram-bot"
        });

        if let Some(serde_json::Value::Object(ctx_map)) = context {
            if let serde_json::Value::Object(ref mut labels_map) = labels {
                labels_map.extend(ctx_map);
            }
        }

        self.log_bot_event("error", error_message, Some(labels)).await;
    }

    async fn send_log_event(&self, event: LogEvent) -> Result<(), reqwest::Error> {
        let response = self.client
            .post(format!("{}/ingest", self.ingest_url))
            .json(&event)
            .send()
            .await?;

        if response.status().is_success() {
            info!("Log event sent to log platform successfully");
        } else {
            error!("Failed to send log event: HTTP {}", response.status());
        }

        Ok(())
    }
}
