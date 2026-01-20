use sqlx::{PgPool, Row};
use uuid::Uuid;
use tracing::{info, error};
use std::collections::HashMap;
use tokio::time::{Duration, Instant};

#[derive(Debug, Clone)]
#[allow(dead_code)]
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

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct User {
    pub id: Uuid,
    pub telegram_user_id: i64,
    pub username: Option<String>,
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

    #[allow(dead_code)]
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

    pub async fn find_or_create_user(&self, telegram_user_id: i64, username: Option<String>) -> Result<Uuid, sqlx::Error> {
        let row = sqlx::query(
            r#"
            INSERT INTO users (telegram_user_id, username, is_active)
            VALUES ($1, $2, true)
            ON CONFLICT (telegram_user_id) 
            DO UPDATE SET username = EXCLUDED.username, updated_at = CURRENT_TIMESTAMP
            RETURNING id
            "#
        )
        .bind(telegram_user_id)
        .bind(username)
        .fetch_one(&self.pool)
        .await?;

        Ok(row.get("id"))
    }

    pub async fn ensure_chat_registered(&self, platform_chat_id: i64, title: Option<String>, telegram_user_id: i64) -> Result<Uuid, sqlx::Error> {
        let user_id = self.find_or_create_user(telegram_user_id, None).await?;
        
        let row = sqlx::query(
            r#"
            INSERT INTO chats (user_id, type, platform_chat_id, title, cleanup_links, is_active)
            VALUES ($1, 'telegram', $2, $3, true, true)
            ON CONFLICT (type, platform_chat_id) 
            DO UPDATE SET 
                title = EXCLUDED.title,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
            "#
        )
        .bind(user_id)
        .bind(platform_chat_id)
        .bind(title)
        .fetch_one(&self.pool)
        .await?;

        let chat_id = row.get("id");
        
        // Clear cache
        {
            let mut cache = self.cache.write().await;
            cache.remove(&platform_chat_id);
        }

        info!("Ensured chat {} registered with ID {}", platform_chat_id, chat_id);
        Ok(chat_id)
    }

    pub async fn increment_processed_messages(&self, platform_chat_id: i64) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            UPDATE chats 
            SET processed_messages = processed_messages + 1, updated_at = CURRENT_TIMESTAMP
            WHERE platform_chat_id = $1 AND type = 'telegram'
            "#
        )
        .bind(platform_chat_id)
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    pub async fn increment_spam_detected(&self, platform_chat_id: i64) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            UPDATE chats 
            SET spam_detected = spam_detected + 1, updated_at = CURRENT_TIMESTAMP
            WHERE platform_chat_id = $1 AND type = 'telegram'
            "#
        )
        .bind(platform_chat_id)
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    pub async fn add_allowed_domain(&self, platform_chat_id: i64, domain: String) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            UPDATE chats 
            SET allowed_link_domains = COALESCE(allowed_link_domains, '[]'::jsonb) || jsonb_build_array($2::text),
                updated_at = CURRENT_TIMESTAMP
            WHERE platform_chat_id = $1 AND type = 'telegram'
            "#
        )
        .bind(platform_chat_id)
        .bind(domain)
        .execute(&self.pool)
        .await?;

        // Clear cache
        {
            let mut cache = self.cache.write().await;
            cache.remove(&platform_chat_id);
        }
        Ok(())
    }

    pub async fn remove_allowed_domain(&self, platform_chat_id: i64, domain: String) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            UPDATE chats 
            SET allowed_link_domains = (
                SELECT jsonb_agg(elem)
                FROM jsonb_array_elements(COALESCE(allowed_link_domains, '[]'::jsonb)) elem
                WHERE elem::text != to_jsonb($2::text)::text
            ),
            updated_at = CURRENT_TIMESTAMP
            WHERE platform_chat_id = $1 AND type = 'telegram'
            "#
        )
        .bind(platform_chat_id)
        .bind(domain)
        .execute(&self.pool)
        .await?;

        // Clear cache
        {
            let mut cache = self.cache.write().await;
            cache.remove(&platform_chat_id);
        }
        Ok(())
    }

    pub async fn get_allowed_domains(&self, platform_chat_id: i64) -> Result<Vec<String>, sqlx::Error> {
        let config = self.get_chat_config(platform_chat_id).await?;
        
        if let Some(config) = config {
            if let Some(serde_json::Value::Array(domains)) = config.allowed_link_domains {
                let domain_list: Vec<String> = domains
                    .iter()
                    .filter_map(|v| v.as_str().map(|s| s.to_string()))
                    .collect();
                return Ok(domain_list);
            }
        }
        
        Ok(Vec::new())
    }
}
