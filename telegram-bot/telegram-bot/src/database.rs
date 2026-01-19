use sqlx::{PgPool, Row};
use uuid::Uuid;
use tracing::{info, error};
use std::collections::HashMap;
use tokio::time::{Duration, Instant};

#[derive(Debug, Clone)]
pub struct ChatConfig {
    pub id: Uuid,
    pub user_id: Uuid,
    pub platform_chat_id: i64,
    pub title: Option<String>,
    pub enable_ai_check: bool,
    pub cleanup_links: bool,
    pub allowed_link_domains: Option<serde_json::Value>,
    pub is_active: bool,
}

pub struct DatabaseClient {
    pool: PgPool,
    cache: tokio::sync::RwLock<HashMap<i64, (ChatConfig, Instant)>>,
    cache_ttl: Duration,
}

impl DatabaseClient {
    pub async fn new(database_url: &str) -> Result<Self, sqlx::Error> {
        let pool = PgPool::connect(database_url).await?;
        
        Ok(Self {
            pool,
            cache: tokio::sync::RwLock::new(HashMap::new()),
            cache_ttl: Duration::from_secs(300), // 5 minutes cache
        })
    }

    pub async fn get_chat_config(&self, platform_chat_id: i64) -> Result<Option<ChatConfig>, sqlx::Error> {
        // Check cache first
        {
            let cache = self.cache.read().await;
            if let Some((config, cached_at)) = cache.get(&platform_chat_id) {
                if cached_at.elapsed() < self.cache_ttl {
                    return Ok(Some(config.clone()));
                }
            }
        }

        // Query database
        let row = sqlx::query(
            r#"
            SELECT id, user_id, platform_chat_id, title, enable_ai_check, 
                   cleanup_links, allowed_link_domains, is_active
            FROM chats 
            WHERE platform_chat_id = $1 AND type = 'telegram' AND is_active = true
            "#
        )
        .bind(platform_chat_id)
        .fetch_optional(&self.pool)
        .await?;

        let config = if let Some(row) = row {
            let config = ChatConfig {
                id: row.get("id"),
                user_id: row.get("user_id"),
                platform_chat_id: row.get("platform_chat_id"),
                title: row.get("title"),
                enable_ai_check: row.get("enable_ai_check"),
                cleanup_links: row.get("cleanup_links"),
                allowed_link_domains: row.get("allowed_link_domains"),
                is_active: row.get("is_active"),
            };

            // Update cache
            {
                let mut cache = self.cache.write().await;
                cache.insert(platform_chat_id, (config.clone(), Instant::now()));
            }

            Some(config)
        } else {
            None
        };

        Ok(config)
    }

    pub async fn is_chat_enabled(&self, platform_chat_id: i64) -> bool {
        match self.get_chat_config(platform_chat_id).await {
            Ok(Some(config)) => config.is_active && config.cleanup_links,
            Ok(None) => false, // Chat not registered, disabled by default
            Err(e) => {
                error!("Database error checking chat config: {}", e);
                false // Fail safe - disable on error
            }
        }
    }

    pub async fn register_chat(&self, platform_chat_id: i64, title: Option<String>, user_id: Uuid) -> Result<Uuid, sqlx::Error> {
        let chat_id = Uuid::new_v4();
        
        sqlx::query(
            r#"
            INSERT INTO chats (id, user_id, type, platform_chat_id, title, enable_ai_check, cleanup_links, is_active)
            VALUES ($1, $2, 'telegram', $3, $4, false, true, true)
            ON CONFLICT (type, platform_chat_id) 
            DO UPDATE SET 
                title = EXCLUDED.title,
                updated_at = CURRENT_TIMESTAMP,
                is_active = true
            "#
        )
        .bind(chat_id)
        .bind(user_id)
        .bind(platform_chat_id)
        .bind(title)
        .execute(&self.pool)
        .await?;

        info!("Registered chat {} with ID {}", platform_chat_id, chat_id);
        
        // Clear cache for this chat
        {
            let mut cache = self.cache.write().await;
            cache.remove(&platform_chat_id);
        }

        Ok(chat_id)
    }

    pub async fn set_chat_enabled(&self, platform_chat_id: i64, enabled: bool) -> Result<bool, sqlx::Error> {
        let result = sqlx::query(
            r#"
            UPDATE chats 
            SET is_active = $1, updated_at = CURRENT_TIMESTAMP
            WHERE platform_chat_id = $2 AND type = 'telegram'
            "#
        )
        .bind(enabled)
        .bind(platform_chat_id)
        .execute(&self.pool)
        .await?;

        // Clear cache for this chat
        {
            let mut cache = self.cache.write().await;
            cache.remove(&platform_chat_id);
        }

        Ok(result.rows_affected() > 0)
    }
}
