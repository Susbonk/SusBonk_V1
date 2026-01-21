#![allow(dead_code)]

use once_cell::sync::Lazy;
use serde::Deserialize;
use std::{env, fmt};
use thiserror::Error;
use tracing::info;

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("config build error: {0}")]
    Build(config::ConfigError),
    #[error("config deserialize error: {0}")]
    Deserialize(config::ConfigError),
    #[error("invalid configuration: {0}")]
    Invalid(String),
}

fn default_log_level() -> String {
    "warn".to_string()
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RunMode {
    Polling,
    Webhook,
}

fn default_run_mode() -> RunMode {
    RunMode::Polling
}

pub static CONFIG: Lazy<Settings> = Lazy::new(|| load().expect("Failed to load configuration"));

#[derive(Clone, Deserialize)]
pub struct Settings {
    #[serde(default = "default_run_mode")]
    pub run_mode: RunMode,

    #[serde(default)]
    pub port: Option<u16>,

    #[serde(default)]
    pub webhook_url: Option<String>,

    #[serde(default = "default_log_level")]
    pub log_level: String,

    #[serde(skip_deserializing, default)]
    pub database: DatabaseSettings,
}

impl Default for DatabaseSettings {
    fn default() -> Self {
        Self::from_env()
    }
}

pub fn load() -> Result<Settings, ConfigError> {
    dotenvy::dotenv().ok();

    let cfg = config::Config::builder()
        .add_source(config::File::with_name("Settings").required(false))
        .add_source(config::Environment::default().try_parsing(true))
        .build()
        .map_err(ConfigError::Build)?;

    let mut settings: Settings = cfg.try_deserialize().map_err(ConfigError::Deserialize)?;

    settings.database = DatabaseSettings::from_env();

    settings.validate()?;
    Ok(settings)
}

impl Settings {
    pub fn validate(&self) -> Result<(), ConfigError> {
        match self.run_mode {
            RunMode::Polling => {}
            RunMode::Webhook => {
                let port = self.port.ok_or_else(|| {
                    ConfigError::Invalid("PORT is required in webhook mode".into())
                })?;
                if !(1..=65535).contains(&port) {
                    return Err(ConfigError::Invalid("port must be 1..=65535".into()));
                }

                if self.webhook_url.as_deref().unwrap_or_default().is_empty() {
                    return Err(ConfigError::Invalid(
                        "WEBHOOK_URL is required in webhook mode".into(),
                    ));
                }
            }
        }
        Ok(())
    }

    pub fn log_effective(&self) {
        if !(cfg!(debug_assertions) || self.log_level.eq_ignore_ascii_case("debug")) {
            return;
        }
        info!(
            "Runtime mode: {} | log_level: {}",
            if cfg!(debug_assertions) { "debug" } else { "release" },
            self.log_level
        );

        println!("Configuration:");
        println!("  Run mode: {:?}", self.run_mode);
        println!("  Port: {:?}", self.port);
        println!("  Webhook URL: {:?}", self.webhook_url);
        println!("  Log level: {}", self.log_level);
        println!("  Database: {:?}", RedactedDbSettings(&self.database));
    }
}

struct Redacted<'a>(&'a Settings);
impl<'a> fmt::Debug for Redacted<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = self.0;
        f.debug_struct("Settings")
            .field("run_mode", &s.run_mode)
            .field("port", &s.port)
            .field("webhook_url", &s.webhook_url)
            .field("log_level", &s.log_level)
            .finish()
    }
}

// -------------------- DatabaseSettings: POSTGRES_* --------------------

fn env_string(name: &str, default: &str) -> String {
    env::var(name).unwrap_or_else(|_| default.to_string())
}
fn env_u16(name: &str, default: u16) -> u16 {
    env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(default)
}
fn env_u32(name: &str, default: u32) -> u32 {
    env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(default)
}
fn env_u64_opt(name: &str) -> Option<u64> {
    match env::var(name) {
        Ok(v) if !v.trim().is_empty() => v.parse().ok(),
        _ => None,
    }
}
fn env_bool(name: &str, default: bool) -> bool {
    env::var(name)
        .ok()
        .map(|v| matches!(v.to_lowercase().as_str(), "1" | "true" | "yes" | "on"))
        .unwrap_or(default)
}

#[derive(Clone, Debug)]
pub struct DatabaseSettings {
    pub host: String,
    pub port: u16,
    pub name: String,
    pub user: String,
    pub password: String,

    pub max_connections: u32,
    pub min_connections: u32,
    pub connect_timeout_secs: u64,
    pub idle_timeout_secs: Option<u64>,
    pub max_lifetime_secs: Option<u64>,

    pub sqlx_logging: bool,
    pub sqlx_logging_level: String,
}

impl DatabaseSettings {
    pub fn from_env() -> Self {
        Self {
            host: env_string("POSTGRES_HOST", "127.0.0.1"),
            port: env_u16("POSTGRES_PORT", 5432),
            name: env_string("POSTGRES_DB", "postgres"),
            user: env_string("POSTGRES_USER", "postgres"),
            password: env_string("POSTGRES_PASSWORD", "password"),

            max_connections: env_u32("POSTGRES_MAX_CONNECTIONS", 10),
            min_connections: env_u32("POSTGRES_MIN_CONNECTIONS", 1),
            connect_timeout_secs: env::var("POSTGRES_CONNECT_TIMEOUT_SECS")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(8),
            idle_timeout_secs: env_u64_opt("POSTGRES_IDLE_TIMEOUT_SECS"),
            max_lifetime_secs: env_u64_opt("POSTGRES_MAX_LIFETIME_SECS"),

            sqlx_logging: env_bool("POSTGRES_SQLX_LOGGING", false),
            sqlx_logging_level: env_string("POSTGRES_SQLX_LOGGING_LEVEL", "info"),
        }
    }

    pub fn to_url(&self) -> String {
        format!(
            "postgres://{user}:{pass}@{host}:{port}/{db}",
            user = self.user,
            pass = self.password,
            host = self.host,
            port = self.port,
            db = self.name,
        )
    }
}

pub struct RedactedDbSettings<'a>(pub &'a DatabaseSettings);

impl<'a> fmt::Debug for RedactedDbSettings<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let db = self.0;
        f.debug_struct("DatabaseSettings")
            .field("host", &db.host)
            .field("port", &db.port)
            .field("name", &db.name)
            .field("user", &db.user)
            .field("max_connections", &db.max_connections)
            .field("min_connections", &db.min_connections)
            .field("connect_timeout_secs", &db.connect_timeout_secs)
            .field("idle_timeout_secs", &db.idle_timeout_secs)
            .field("max_lifetime_secs", &db.max_lifetime_secs)
            .field("sqlx_logging", &db.sqlx_logging)
            .field("sqlx_logging_level", &db.sqlx_logging_level)
            .finish()
    }
}
