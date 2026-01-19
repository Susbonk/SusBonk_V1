use once_cell::sync::Lazy;
use std::env;

#[derive(Debug, Clone)]
pub enum RunMode {
    Polling,
    Webhook,
}

impl RunMode {
    fn from_env() -> Self {
        match env::var("RUN_MODE").unwrap_or_default().to_lowercase().as_str() {
            "webhook" => RunMode::Webhook,
            _ => RunMode::Polling,
        }
    }
}

#[derive(Debug, Clone)]
pub struct DatabaseSettings {
    pub host: String,
    pub port: u16,
    pub user: String,
    pub password: String,
    pub database: String,
    pub max_connections: u32,
    pub min_connections: u32,
}

impl DatabaseSettings {
    fn from_env() -> Self {
        Self {
            host: env::var("POSTGRES_HOST").unwrap_or_else(|_| "localhost".to_string()),
            port: env::var("POSTGRES_PORT")
                .unwrap_or_else(|_| "5432".to_string())
                .parse()
                .unwrap_or(5432),
            user: env::var("POSTGRES_USER").expect("POSTGRES_USER must be set"),
            password: env::var("POSTGRES_PASSWORD").expect("POSTGRES_PASSWORD must be set"),
            database: env::var("POSTGRES_DB").expect("POSTGRES_DB must be set"),
            max_connections: env::var("POSTGRES_MAX_CONNECTIONS")
                .unwrap_or_else(|_| "10".to_string())
                .parse()
                .unwrap_or(10),
            min_connections: env::var("POSTGRES_MIN_CONNECTIONS")
                .unwrap_or_else(|_| "1".to_string())
                .parse()
                .unwrap_or(1),
        }
    }

    pub fn connection_string(&self) -> String {
        format!(
            "postgresql://{}:{}@{}:{}/{}",
            self.user, self.password, self.host, self.port, self.database
        )
    }
}

#[derive(Debug, Clone)]
pub struct RedisSettings {
    pub url: String,
}

impl RedisSettings {
    fn from_env() -> Self {
        Self {
            url: env::var("REDIS_URL").unwrap_or_else(|_| "redis://localhost:6379".to_string()),
        }
    }
}

#[derive(Debug, Clone)]
pub struct TelegramSettings {
    pub token: String,
    pub username: Option<String>,
}

impl TelegramSettings {
    fn from_env() -> Self {
        Self {
            token: env::var("TELOXIDE_TOKEN")
                .or_else(|_| env::var("TELEGRAM_BOT_TOKEN"))
                .expect("TELOXIDE_TOKEN or TELEGRAM_BOT_TOKEN must be set"),
            username: env::var("TELEGRAM_BOT_USERNAME").ok(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct WebhookSettings {
    pub url: String,
    pub port: u16,
}

impl WebhookSettings {
    fn from_env() -> Self {
        Self {
            url: env::var("WEBHOOK_URL").unwrap_or_default(),
            port: env::var("WEBHOOK_PORT")
                .unwrap_or_else(|_| "8443".to_string())
                .parse()
                .unwrap_or(8443),
        }
    }
}

#[derive(Debug, Clone)]
pub struct LogSettings {
    pub level: String,
    pub ingest_url: String,
}

impl LogSettings {
    fn from_env() -> Self {
        Self {
            level: env::var("LOG_LEVEL").unwrap_or_else(|_| "info".to_string()),
            ingest_url: env::var("INGEST_URL")
                .or_else(|_| env::var("OS_INGEST_URL"))
                .unwrap_or_else(|_| "http://localhost:8080".to_string()),
        }
    }
}

#[derive(Debug, Clone)]
pub struct Config {
    pub run_mode: RunMode,
    pub database: DatabaseSettings,
    pub redis: RedisSettings,
    pub telegram: TelegramSettings,
    pub webhook: WebhookSettings,
    pub log: LogSettings,
    pub health_port: u16,
}

impl Config {
    fn load() -> Self {
        Self {
            run_mode: RunMode::from_env(),
            database: DatabaseSettings::from_env(),
            redis: RedisSettings::from_env(),
            telegram: TelegramSettings::from_env(),
            webhook: WebhookSettings::from_env(),
            log: LogSettings::from_env(),
            health_port: env::var("HEALTH_PORT")
                .unwrap_or_else(|_| "8081".to_string())
                .parse()
                .unwrap_or(8081),
        }
    }
}

pub static CONFIG: Lazy<Config> = Lazy::new(|| Config::load());
