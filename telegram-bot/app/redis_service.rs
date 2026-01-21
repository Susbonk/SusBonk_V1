use chrono;
use redis::{AsyncCommands, Client, RedisResult};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub struct DeletedMessage {
    pub job_id: String,
    pub chat_id: i64,
    pub chat_uuid: String,
    pub telegram_user_id: i64,
    pub user_state_uuid: Option<String>,
    pub nickname: Option<String>,
    pub message_text: String,
    pub timestamp: i64,
}

pub struct RedisService {
    client: Client,
}

impl RedisService {
    pub fn new(redis_url: &str) -> RedisResult<Self> {
        let client = Client::open(redis_url)?;
        Ok(Self { client })
    }

    pub async fn store_deleted_message(
        &self,
        chat_uuid: &str,
        chat_id: i64,
        telegram_user_id: i64,
        user_state_uuid: Option<String>,
        nickname: Option<String>,
        message_text: String,
    ) -> RedisResult<String> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;

        let job_id = Uuid::new_v4().to_string();
        let timestamp = chrono::Utc::now().timestamp();

        let deleted_msg = DeletedMessage {
            job_id: job_id.clone(),
            chat_id,
            chat_uuid: chat_uuid.to_string(),
            telegram_user_id,
            user_state_uuid,
            nickname,
            message_text,
            timestamp,
        };

        let payload = serde_json::to_string(&deleted_msg).unwrap();

        // Store in Redis stream with 24-hour expiration
        let stream_key = format!("deleted_messages:{}", chat_uuid);

        let _: String = conn
            .xadd(
                &stream_key,
                "*",
                &[("job_id", &job_id), ("payload", &payload)],
            )
            .await?;

        // TODO: Move to environment variable
        // Set expiration for the stream (24 hours = 86400 seconds)
        let _: bool = conn.expire(&stream_key, 86400).await?;

        Ok(job_id)
    }
}
