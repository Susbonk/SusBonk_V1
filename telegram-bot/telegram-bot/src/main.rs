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
            bot.send_message(chat_id, "🐕 SusBonk Bot Commands:\n/start - Activate bot\n/help - Show this help\n/enable - Enable spam detection (admin only)\n/disable - Disable spam detection (admin only)").await?;
        }
        Command::Enable => {
            if !is_user_admin(&bot, chat_id, user_id).await {
                bot.send_message(chat_id, "❌ Only group administrators can enable spam detection").await?;
                success = false;
            } else {
                match state.db_client.set_chat_enabled(chat_id.0, true).await {
                    Ok(true) => {
                        bot.send_message(chat_id, "✅ Spam detection enabled for this chat").await?;
                    }
                    Ok(false) => {
                        bot.send_message(chat_id, "❌ Chat not found. Please contact support.").await?;
                        success = false;
                    }
                    Err(e) => {
                        error!("Database error enabling chat: {}", e);
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
                        bot.send_message(chat_id, "❌ Chat not found. Please contact support.").await?;
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

async fn handle_message(msg: Message, state: Arc<AppState>) -> ResponseResult<()> {
    let chat_id = msg.chat.id.0;
    
    // Check if spam detection is enabled for this chat
    if !state.db_client.is_chat_enabled(chat_id).await {
        return Ok(());
    }

    if let Some(text) = msg.text() {
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
                detected_content: detection.detected_url,
                confidence: detection.confidence,
            };
            
            info!("Detected spam: {} (confidence: {:.2})", detection.reason, detection.confidence);
            
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
    
    // Create consumer group for spam events
    if let Err(e) = state.redis_client.create_consumer_group("spam_events:*", "spam_processors").await {
        error!("Failed to create consumer group: {}", e);
    }
    
    // Start health check server
    let health_app = Router::new()
        .route("/health", get(health_handler));
    
    let health_addr = format!("0.0.0.0:{}", CONFIG.health_port);
    info!("Health check server listening on {}", health_addr);
    
    tokio::spawn(async move {
        let listener = TcpListener::bind(&health_addr).await.unwrap();
        axum::serve(listener, health_app).await.unwrap();
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
                    move |msg| {
                        let state = state.clone();
                        async move { handle_message(msg, state).await }
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
