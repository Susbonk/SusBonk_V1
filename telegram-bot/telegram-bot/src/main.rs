mod database;
mod link_detector;
mod log_client;
mod redis_client;
mod types;

use config::CONFIG;
use teloxide::{prelude::*, utils::command::BotCommands};
use tracing::{info, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use axum::{routing::get, Router, Json};
use std::sync::Arc;
use tokio::net::TcpListener;
use chrono::Utc;
use types::{SpamEvent, UserInfo};
use database::DatabaseClient;
use link_detector::LinkDetector;
use log_client::LogPlatformClient;
use redis_client::RedisStreamsClient;

#[derive(BotCommands, Clone, Debug)]
#[command(rename_rule = "lowercase", description = "SusBonk Bot Commands")]
enum Command {
    #[command(description = "Start the bot")]
    Start,
    #[command(description = "Show help")]
    Help,
    #[command(description = "Enable spam detection for this chat")]
    Enable,
    #[command(description = "Disable spam detection for this chat")]
    Disable,
    #[command(description = "Add domain to whitelist (e.g., /whitelist_add example.com)")]
    WhitelistAdd(String),
    #[command(description = "Remove domain from whitelist")]
    WhitelistRemove(String),
    #[command(description = "Show whitelisted domains")]
    WhitelistList,
}

struct AppState {
    redis_client: RedisStreamsClient,
    db_client: DatabaseClient,
    link_detector: LinkDetector,
    log_client: LogPlatformClient,
}

async fn health_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ok", "service": "telegram-bot"}))
}

async fn is_user_admin(bot: &Bot, chat_id: ChatId, user_id: UserId) -> bool {
    match bot.get_chat_member(chat_id, user_id).await {
        Ok(member) => matches!(member.kind, teloxide::types::ChatMemberKind::Owner(_) | teloxide::types::ChatMemberKind::Administrator(_)),
        Err(_) => false,
    }
}

async fn handle_command(bot: Bot, msg: Message, cmd: Command, state: Arc<AppState>) -> ResponseResult<()> {
    let chat_id = msg.chat.id;
    let user_id = match msg.from {
        Some(ref user) => user.id,
        None => {
            bot.send_message(chat_id, "❌ Unable to identify user").await?;
            return Ok(());
        }
    };

    let command_name = format!("{:?}", cmd).to_lowercase();
    let mut success = true;

    match cmd {
        Command::Start => {
            bot.send_message(chat_id, "🐕 SusBonk Bot is now active! I'll silently monitor for spam links.\n\nUse /enable to activate spam detection for this chat.").await?;
        }
        Command::Help => {
            bot.send_message(chat_id, "🐕 SusBonk Bot Commands:\n/start - Activate bot\n/help - Show this help\n/enable - Enable spam detection (admin only)\n/disable - Disable spam detection (admin only)\n/whitelist_add <domain> - Add domain to whitelist\n/whitelist_remove <domain> - Remove domain from whitelist\n/whitelist_list - Show whitelisted domains").await?;
        }
        Command::Enable => {
            if !is_user_admin(&bot, chat_id, user_id).await {
                bot.send_message(chat_id, "❌ Only group administrators can enable spam detection").await?;
                success = false;
            } else {
                let chat_title = msg.chat.title().map(|s| s.to_string());
                match state.db_client.ensure_chat_registered(chat_id.0, chat_title, user_id.0 as i64).await {
                    Ok(_) => {
                        match state.db_client.set_chat_enabled(chat_id.0, true).await {
                            Ok(_) => {
                                bot.send_message(chat_id, "✅ Chat registered and spam detection enabled").await?;
                            }
                            Err(e) => {
                                error!("Database error enabling chat: {}", e);
                                bot.send_message(chat_id, "❌ Database error. Please try again later.").await?;
                                success = false;
                            }
                        }
                    }
                    Err(e) => {
                        error!("Database error registering chat: {}", e);
                        bot.send_message(chat_id, "❌ Database error. Please try again later.").await?;
                        success = false;
                    }
                }
            }
        }
        Command::Disable => {
            if !is_user_admin(&bot, chat_id, user_id).await {
                bot.send_message(chat_id, "❌ Only group administrators can disable spam detection").await?;
                success = false;
            } else {
                match state.db_client.set_chat_enabled(chat_id.0, false).await {
                    Ok(true) => {
                        bot.send_message(chat_id, "🔕 Spam detection disabled for this chat").await?;
                    }
                    Ok(false) => {
                        bot.send_message(chat_id, "❌ Chat not registered. Use /enable first.").await?;
                        success = false;
                    }
                    Err(e) => {
                        error!("Database error disabling chat: {}", e);
                        bot.send_message(chat_id, "❌ Database error. Please try again later.").await?;
                        success = false;
                    }
                }
            }
        }
        Command::WhitelistAdd(domain) => {
            if !is_user_admin(&bot, chat_id, user_id).await {
                bot.send_message(chat_id, "❌ Only group administrators can manage whitelist").await?;
                success = false;
            } else {
                let clean_domain = domain.trim().to_lowercase();
                if clean_domain.is_empty() {
                    bot.send_message(chat_id, "❌ Please provide a domain (e.g., /whitelist_add example.com)").await?;
                    success = false;
                } else {
                    match state.db_client.add_allowed_domain(chat_id.0, clean_domain.clone()).await {
                        Ok(_) => {
                            bot.send_message(chat_id, format!("✅ Added {} to whitelist", clean_domain)).await?;
                        }
                        Err(e) => {
                            error!("Database error adding domain: {}", e);
                            bot.send_message(chat_id, "❌ Database error. Please try again later.").await?;
                            success = false;
                        }
                    }
                }
            }
        }
        Command::WhitelistRemove(domain) => {
            if !is_user_admin(&bot, chat_id, user_id).await {
                bot.send_message(chat_id, "❌ Only group administrators can manage whitelist").await?;
                success = false;
            } else {
                let clean_domain = domain.trim().to_lowercase();
                if clean_domain.is_empty() {
                    bot.send_message(chat_id, "❌ Please provide a domain (e.g., /whitelist_remove example.com)").await?;
                    success = false;
                } else {
                    match state.db_client.remove_allowed_domain(chat_id.0, clean_domain.clone()).await {
                        Ok(_) => {
                            bot.send_message(chat_id, format!("✅ Removed {} from whitelist", clean_domain)).await?;
                        }
                        Err(e) => {
                            error!("Database error removing domain: {}", e);
                            bot.send_message(chat_id, "❌ Database error. Please try again later.").await?;
                            success = false;
                        }
                    }
                }
            }
        }
        Command::WhitelistList => {
            match state.db_client.get_allowed_domains(chat_id.0).await {
                Ok(domains) => {
                    if domains.is_empty() {
                        bot.send_message(chat_id, "📋 No whitelisted domains").await?;
                    } else {
                        let list = domains.join("\n• ");
                        bot.send_message(chat_id, format!("📋 Whitelisted domains:\n• {}", list)).await?;
                    }
                }
                Err(e) => {
                    error!("Database error getting domains: {}", e);
                    bot.send_message(chat_id, "❌ Database error. Please try again later.").await?;
                    success = false;
                }
            }
        }
    }

    // Log command execution
    state.log_client.log_command_execution(
        chat_id.0,
        &command_name,
        user_id.0 as i64,
        success
    ).await;

    Ok(())
}

async fn handle_message(bot: Bot, msg: Message, state: Arc<AppState>) -> ResponseResult<()> {
    let chat_id = msg.chat.id.0;
    let message_id = msg.id;
    
    // Check if spam detection is enabled for this chat
    if !state.db_client.is_chat_enabled(chat_id).await {
        return Ok(());
    }

    if let Some(text) = msg.text() {
        // Increment processed messages counter
        if let Err(e) = state.db_client.increment_processed_messages(chat_id).await {
            error!("Failed to increment processed messages: {}", e);
        }
        
        info!("Processing message in chat {}: {}", chat_id, text);
        
        // Get chat configuration for link detection
        let chat_config = match state.db_client.get_chat_config(chat_id).await {
            Ok(config) => config,
            Err(e) => {
                error!("Failed to get chat config: {}", e);
                return Ok(());
            }
        };
        
        // Detect suspicious links
        let detections = state.link_detector.detect_links(text, chat_config.as_ref());
        
        if !detections.is_empty() {
            // Increment spam detected counter
            if let Err(e) = state.db_client.increment_spam_detected(chat_id).await {
                error!("Failed to increment spam detected: {}", e);
            }
        }
        
        for detection in detections {
            let user_info = UserInfo {
                id: msg.from.as_ref().map(|u| u.id.0 as i64).unwrap_or(0),
                username: msg.from.as_ref().and_then(|u| u.username.clone()),
                first_name: msg.from.as_ref().map(|u| u.first_name.clone()),
            };
            
            let spam_event = SpamEvent {
                timestamp: Utc::now(),
                chat_id,
                user: user_info,
                detection_type: detection.detection_type.clone(),
                message_text: text.to_string(),
                detected_content: detection.detected_url.clone(),
                confidence: detection.confidence,
            };
            
            info!("Detected spam: {} (confidence: {:.2})", detection.reason, detection.confidence);
            
            // Delete spam message if confidence is high
            if detection.confidence >= 0.8 {
                match bot.delete_message(msg.chat.id, message_id).await {
                    Ok(_) => {
                        info!("Deleted spam message {} in chat {}", message_id, chat_id);
                        
                        // Notify about deletion (optional, can be made configurable)
                        let notification = format!(
                            "🚨 Spam detected and removed\nReason: {}\nConfidence: {:.0}%",
                            detection.reason,
                            detection.confidence * 100.0
                        );
                        if let Err(e) = bot.send_message(msg.chat.id, notification).await {
                            error!("Failed to send deletion notification: {}", e);
                        }
                    }
                    Err(e) => {
                        error!("Failed to delete spam message: {}", e);
                    }
                }
            }
            
            // Log to Redis Streams
            if let Err(e) = state.redis_client.log_spam_event(&spam_event).await {
                error!("Failed to log spam event: {}", e);
                state.log_client.log_error(
                    &format!("Failed to log spam event to Redis: {}", e),
                    Some(serde_json::json!({
                        "chat_id": chat_id,
                        "detection_type": format!("{:?}", detection.detection_type)
                    }))
                ).await;
            }
            
            // Log to structured logging platform
            state.log_client.log_spam_detection(
                chat_id,
                &format!("{:?}", detection.detection_type),
                detection.confidence
            ).await;
        }
    }
    Ok(())
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| format!("telegram_bot=debug,{}", CONFIG.log.level).into()),
        )
        .with(tracing_subscriber::fmt::layer().json())
        .init();

    info!("Starting telegram-bot service");
    info!("Run mode: {:?}", CONFIG.run_mode);

    let bot = Bot::new(&CONFIG.telegram.token);
    let redis_client = RedisStreamsClient::new(&CONFIG.redis.url)?;
    let db_client = DatabaseClient::new(&CONFIG.database.connection_string()).await?;
    let log_client = LogPlatformClient::new(CONFIG.log.ingest_url.clone());
    
    let state = Arc::new(AppState {
        redis_client,
        db_client,
        link_detector: LinkDetector::new(),
        log_client,
    });
    
    // Log startup
    state.log_client.log_startup().await;
    
    // Create consumer group for spam events (use fixed stream name)
    if let Err(e) = state.redis_client.create_consumer_group("spam_events", "spam_processors").await {
        error!("Failed to create consumer group (may already exist): {}", e);
    }
    
    // Start health check server
    let health_app = Router::new()
        .route("/health", get(health_handler));
    
    let health_addr = format!("0.0.0.0:{}", CONFIG.health_port);
    info!("Health check server listening on {}", health_addr);
    
    tokio::spawn(async move {
        match TcpListener::bind(&health_addr).await {
            Ok(listener) => {
                info!("Health server bound successfully");
                if let Err(e) = axum::serve(listener, health_app).await {
                    error!("Health server error: {}", e);
                }
            }
            Err(e) => {
                error!("Failed to bind health server on {}: {}", health_addr, e);
            }
        }
    });

    // Start bot
    info!("Starting Telegram bot");
    
    let use_webhooks = matches!(CONFIG.run_mode, config::RunMode::Webhook);
    
    if use_webhooks {
        info!("Webhook mode requested but not implemented in this teloxide version");
        info!("Falling back to long polling mode");
        
        // TODO: Implement webhook support when teloxide API is available
        // For now, fall back to polling
    }
    
    info!("Starting bot with long polling");
    
    let handler = dptree::entry()
        .branch(
            Update::filter_message()
                .filter_command::<Command>()
                .endpoint({
                    let state = state.clone();
                    move |bot, msg, cmd| {
                        let state = state.clone();
                        async move { handle_command(bot, msg, cmd, state).await }
                    }
                })
        )
        .branch(
            Update::filter_message()
                .endpoint({
                    let state = state.clone();
                    move |bot, msg| {
                        let state = state.clone();
                        async move { handle_message(bot, msg, state).await }
                    }
                })
        );

    Dispatcher::builder(bot, handler)
        .enable_ctrlc_handler()
        .build()
        .dispatch()
        .await;

    Ok(())
}
