use crate::services;
use anyhow::Result;
use sea_orm::DatabaseConnection;
use teloxide::types::{ChatId, Message, MessageEntity, MessageId, UserId};
use tokio::sync::mpsc;

#[derive(Clone, Debug)]
pub struct GroupWorkItem {
    pub chat_id: ChatId,
    pub message_id: MessageId,
    pub text: String,
    pub entities: Vec<MessageEntity>,
    pub user_id: UserId,
    pub user_nickname: Option<String>,
    pub is_trusted_or_owner: bool,
}

/// Enqueue group/supergroup text messages for background processing.
/// Keeps the handler fast: no heavy work, no logging.
pub async fn handle_group_enqueue(
    bot: teloxide::Bot,
    db: DatabaseConnection,
    msg: Message,
    tx: mpsc::Sender<GroupWorkItem>,
) -> Result<()> {
    // Safe to unwrap: this handler is only called for messages with text
    let text = msg.text().unwrap().to_string();
    let chat_id = msg.chat.id;
    let message_id = msg.id;
    let user_id = msg.from.as_ref().map(|u| u.id).unwrap_or(UserId(0));

    // Update chat link if empty (fire and forget)
    let _ = services::update_chat_link_if_empty(&db, &bot, chat_id.0).await;

    // Ensure user state exists and check if user is trusted or owner
    let is_trusted_or_owner = if let Some(user) = msg.from.as_ref() {
        let is_owner = services::is_chat_owner(&db, user.id.0 as i64, chat_id.0)
            .await
            .unwrap_or(false);

        if !is_owner {
            let _ = services::ensure_user_state(&db, user.id.0 as i64, chat_id.0).await;
            let is_trusted = services::is_user_trusted(&db, user.id.0 as i64, chat_id.0)
                .await
                .unwrap_or(false);
            is_trusted
        } else {
            true
        }
    } else {
        false
    };

    // Own the entities so they can cross task boundaries safely
    let entities: Vec<MessageEntity> = msg
        .entities()
        .map(|entities| entities.to_vec())
        .unwrap_or_default();

    // Extract user nickname
    let user_nickname = msg.from.as_ref().and_then(|user| {
        user.username.clone().or_else(|| {
            // Fallback to first_name + last_name if no username
            let first = user.first_name.clone();
            let last = user.last_name.clone().unwrap_or_default();
            if last.is_empty() {
                Some(first)
            } else {
                Some(format!("{} {}", first, last))
            }
        })
    });

    // Best-effort enqueue: if full/closed, drop silently
    let _ = tx
        .send(GroupWorkItem {
            chat_id,
            message_id,
            text,
            entities,
            user_id,
            user_nickname,
            is_trusted_or_owner,
        })
        .await;

    Ok(())
}
