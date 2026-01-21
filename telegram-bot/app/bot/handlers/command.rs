use crate::services::{self, ConnectionResult};
use anyhow::Result;
use sea_orm::DatabaseConnection;
use teloxide::utils::command::BotCommands;
use teloxide::{prelude::*, types::Message};
use uuid::Uuid;

#[derive(BotCommands, Clone)]
#[command(rename_rule = "lowercase", description = "Available commands:")]
pub enum Command {
    #[command(description = "start the bot")]
    Start(String), // payload: e.g. /start <payload>"
    #[command(description = "show help")]
    Help,
}

pub async fn handle_command(
    bot: teloxide::Bot,
    msg: Message,
    cmd: Command,
    db: &DatabaseConnection,
) -> Result<()> {
    match cmd {
        Command::Start(payload) => {
            let p = payload.trim();

            if let Ok(uuid) = Uuid::parse_str(p) {
                let telegram_user_id = msg.from.unwrap().id.0 as i64;

                match services::connect_telegram_to_account(db, uuid, telegram_user_id).await {
                    Ok(ConnectionResult::Success) => {
                        bot.send_message(
                            msg.chat.id,
                            "✅ Account successfully connected to Telegram!",
                        )
                        .await?;
                    }
                    Ok(ConnectionResult::AlreadyConnectedToSameAccount) => {
                        bot.send_message(
                            msg.chat.id,
                            "ℹ️ Your Telegram is already connected to this account.",
                        )
                        .await?;
                    }
                    Ok(ConnectionResult::AlreadyConnectedToOtherAccount) => {
                        bot.send_message(
                            msg.chat.id,
                            "❌ This Telegram account is already assigned to somebody else.",
                        )
                        .await?;
                    }
                    Ok(ConnectionResult::UserNotFound) => {
                        bot.send_message(
                            msg.chat.id,
                            "❌ Invalid connection token or account not found.",
                        )
                        .await?;
                    }
                    Err(_) => {
                        bot.send_message(
                            msg.chat.id,
                            "❌ Connection failed. Please try again later.",
                        )
                        .await?;
                    }
                }
            } else {
                bot.send_message(
                    msg.chat.id,
                    "Hello! I'm a spam cleaning bot, to use me visit https://link.com or TG Mini App ...",
                )
                .await?;
            }
        }
        Command::Help => {
            bot.send_message(
                msg.chat.id,
                "I'm a simple bot!\n\nAvailable commands:\n/start - Start the bot\n/help - Show this help message",
            )
            .await?;
        }
    }
    Ok(())
}
