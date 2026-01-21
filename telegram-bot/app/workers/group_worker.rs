use sea_orm::{ActiveModelTrait, ColumnTrait, DatabaseConnection, EntityTrait, QueryFilter, Set};
use std::sync::Arc;
use teloxide::prelude::*;
use tokio::sync::{Mutex, mpsc};

use crate::bot::handlers::GroupWorkItem;
use crate::bot::helpers::delete_message_by_ids;
use crate::bot::utils::extract_message_with_links;
use crate::redis_service::RedisService;
use entity::{chats, user_states};
use uuid;

async fn get_chat_uuid_by_platform_id(
    db: &DatabaseConnection,
    platform_chat_id: i64,
) -> Result<Option<uuid::Uuid>, sea_orm::DbErr> {
    use sea_orm::{ColumnTrait, EntityTrait, QueryFilter};
    
    let chat = chats::Entity::find()
        .filter(chats::Column::PlatformChatId.eq(platform_chat_id))
        .one(db)
        .await?;
    
    Ok(chat.map(|c| c.id))
}

async fn get_user_state_uuid(
    db: &DatabaseConnection,
    external_user_id: i64,
    chat_uuid: uuid::Uuid,
) -> Result<Option<uuid::Uuid>, sea_orm::DbErr> {
    use sea_orm::{ColumnTrait, EntityTrait, QueryFilter};
    
    let user_state = user_states::Entity::find()
        .filter(user_states::Column::ExternalUserId.eq(external_user_id))
        .filter(user_states::Column::ChatId.eq(chat_uuid))
        .one(db)
        .await?;
    
    Ok(user_state.map(|u| u.id))
}

#[derive(Debug)]
struct ChatData {
    enable_ai_check: bool,
    cleanup_mentions: bool,
    cleanup_emojis: bool,
    cleanup_links: bool,
    cleanup_emails: bool,
    prompts: Vec<String>,
    custom_prompts: Vec<String>,
    max_emoji_count: i32,
    allowed_mentions: Option<Vec<String>>,
    allowed_link_domains: Option<Vec<String>>,
}

pub async fn run_group_worker(
    worker_id: usize,
    bot: Bot,
    rx: Arc<Mutex<mpsc::Receiver<GroupWorkItem>>>,
    db: DatabaseConnection,
) {
    tracing::info!(worker = worker_id, "group worker started");

    // Initialize Redis service
    let redis_url =
        std::env::var("REDIS_URL").unwrap_or_else(|_| "redis://localhost:6379".to_string());
    let redis_service = match RedisService::new(&redis_url) {
        Ok(service) => Some(service),
        Err(e) => {
            tracing::warn!(worker = worker_id, error = %e, "failed to connect to Redis, deleted messages won't be stored");
            None
        }
    };

    loop {
        let item = {
            let mut guard = rx.lock().await;
            guard.recv().await
        };

        let Some(item) = item else {
            tracing::info!(worker = worker_id, "group worker stopped (channel closed)");
            break;
        };

        tracing::info!(
            worker = worker_id,
            chat_id = ?item.chat_id,
            message_id = ?item.message_id,
            user_id = ?item.user_id,
            text = %item.text,
            entities = ?item.entities,
            "received group message"
        );

        // Fetch chat data in single query
        let chat_data = match fetch_chat_data(&db, item.chat_id.0).await {
            Ok(Some(data)) => data,
            Ok(None) => {
                tracing::warn!(
                    worker = worker_id,
                    chat_id = ?item.chat_id,
                    "chat not found in database, skipping checks"
                );
                continue;
            }
            Err(e) => {
                tracing::error!(
                    worker = worker_id,
                    chat_id = ?item.chat_id,
                    error = %e,
                    "failed to fetch chat data"
                );
                continue;
            }
        };

        // Skip checks for trusted users or owners
        if item.is_trusted_or_owner {
            tracing::info!(
                worker = worker_id,
                chat_id = ?item.chat_id,
                user_id = ?item.user_id,
                is_trusted_or_owner = item.is_trusted_or_owner,
                "skipping checks for trusted user or owner"
            );

            // Update processed messages count for chat
            let _ =
                update_message_counts(&db, item.chat_id.0, item.user_id.0 as i64, &chat_data, true)
                    .await;
            continue;
        }

        // Print prompts and custom prompts for now
        if !chat_data.prompts.is_empty() {
            tracing::info!(
                worker = worker_id,
                chat_id = ?item.chat_id,
                prompts = ?chat_data.prompts,
                "chat prompts"
            );
        }
        if !chat_data.custom_prompts.is_empty() {
            tracing::info!(
                worker = worker_id,
                chat_id = ?item.chat_id,
                custom_prompts = ?chat_data.custom_prompts,
                "chat custom prompts"
            );
        }

        // Apply conditional checks based on chat settings
        if let Some(trigger) = detect_trigger_conditional(&item.text, &item.entities, &chat_data) {
            tracing::info!(
                worker = worker_id,
                chat_id = ?item.chat_id,
                message_id = ?item.message_id,
                trigger = ?trigger,
                "deleting message due to moderation trigger"
            );

            // Store deleted message in Redis before deletion
            if let Some(ref redis) = redis_service {
                let message_with_links = extract_message_with_links(&item.text, &item.entities);
                
                // Get chat UUID from database
                let (chat_uuid, chat_uuid_obj) = match get_chat_uuid_by_platform_id(&db, item.chat_id.0).await {
                    Ok(Some(uuid)) => (uuid.to_string(), Some(uuid)),
                    Ok(None) => {
                        tracing::warn!(
                            worker = worker_id,
                            chat_id = ?item.chat_id,
                            "chat not found in database, using platform_id as fallback"
                        );
                        (item.chat_id.0.abs().to_string(), None)
                    }
                    Err(e) => {
                        tracing::warn!(
                            worker = worker_id,
                            chat_id = ?item.chat_id,
                            error = %e,
                            "failed to get chat UUID, using platform_id as fallback"
                        );
                        (item.chat_id.0.abs().to_string(), None)
                    }
                };

                // Get user state UUID if chat UUID is available
                let user_state_uuid = if let Some(chat_uuid_obj) = chat_uuid_obj {
                    match get_user_state_uuid(&db, item.user_id.0 as i64, chat_uuid_obj).await {
                        Ok(Some(uuid)) => Some(uuid.to_string()),
                        Ok(None) => None,
                        Err(e) => {
                            tracing::warn!(
                                worker = worker_id,
                                user_id = ?item.user_id,
                                chat_id = ?item.chat_id,
                                error = %e,
                                "failed to get user state UUID"
                            );
                            None
                        }
                    }
                } else {
                    None
                };

                match redis
                    .store_deleted_message(
                        &chat_uuid,
                        item.chat_id.0,
                        item.user_id.0 as i64,
                        user_state_uuid,
                        item.user_nickname.clone(),
                        message_with_links,
                    )
                    .await
                {
                    Ok(job_id) => {
                        tracing::info!(
                            worker = worker_id,
                            chat_id = ?item.chat_id,
                            message_id = ?item.message_id,
                            job_id = %job_id,
                            "stored deleted message in Redis"
                        );
                    }
                    Err(e) => {
                        tracing::warn!(
                            worker = worker_id,
                            chat_id = ?item.chat_id,
                            message_id = ?item.message_id,
                            error = %e,
                            "failed to store deleted message in Redis"
                        );
                    }
                }
            }

            match delete_message_by_ids(&bot, item.chat_id, item.message_id).await {
                Ok(_) => {
                    tracing::info!(
                        worker = worker_id,
                        chat_id = ?item.chat_id,
                        message_id = ?item.message_id,
                        trigger = ?trigger,
                        "deleted message"
                    );
                }
                Err(e) => {
                    tracing::warn!(
                        worker = worker_id,
                        chat_id = ?item.chat_id,
                        message_id = ?item.message_id,
                        trigger = ?trigger,
                        error = %e,
                        "failed to delete message"
                    );
                }
            }

            continue;
        }

        // Message passed all checks - no action needed
        tracing::info!(
            worker = worker_id,
            chat_id = ?item.chat_id,
            message_id = ?item.message_id,
            "message passed all moderation checks"
        );

        // Update processed messages count for chat
        let _ = update_message_counts(
            &db,
            item.chat_id.0,
            item.user_id.0 as i64,
            &chat_data,
            false,
        )
        .await;
    }
}

async fn fetch_chat_data(
    db: &DatabaseConnection,
    platform_chat_id: i64,
) -> Result<Option<ChatData>, sea_orm::DbErr> {
    // Single query to get chat
    let chat = chats::Entity::find()
        .filter(chats::Column::PlatformChatId.eq(platform_chat_id))
        .one(db)
        .await?;

    let Some(chat) = chat else {
        return Ok(None);
    };

    // Get prompts for this chat (placeholder for now)
    let prompts: Vec<String> = vec![];
    let custom_prompts: Vec<String> = vec![];

    Ok(Some(ChatData {
        enable_ai_check: chat.enable_ai_check,
        cleanup_mentions: chat.cleanup_mentions,
        cleanup_emojis: chat.cleanup_emojis,
        cleanup_links: chat.cleanup_links,
        cleanup_emails: chat.cleanup_emails,
        prompts,
        custom_prompts,
        max_emoji_count: chat.max_emoji_count,
        allowed_mentions: chat
            .allowed_mentions
            .as_ref()
            .and_then(|json| serde_json::from_value(json.clone()).ok()),
        allowed_link_domains: chat
            .allowed_link_domains
            .as_ref()
            .and_then(|json| serde_json::from_value(json.clone()).ok()),
    }))
}

async fn update_message_counts(
    db: &DatabaseConnection,
    chat_id: i64,
    user_id: i64,
    chat_data: &ChatData,
    is_trusted_or_owner: bool,
) -> Result<(), sea_orm::DbErr> {
    // Update processed messages count for chat
    let chat = chats::Entity::find()
        .filter(chats::Column::PlatformChatId.eq(chat_id))
        .one(db)
        .await?;

    if let Some(chat) = chat {
        let chat_id_uuid = chat.id;
        let mut chat_active: chats::ActiveModel = chat.into();
        chat_active.processed_messages = Set(chat_active.processed_messages.unwrap() + 1);
        chat_active.update(db).await?;

        // Update user valid messages if AI checks are disabled or user is trusted/owner
        if !chat_data.enable_ai_check || is_trusted_or_owner {
            if !is_trusted_or_owner {
                // Only update user state for non-owners
                let user_state = user_states::Entity::find()
                    .filter(user_states::Column::ExternalUserId.eq(user_id))
                    .filter(user_states::Column::ChatId.eq(chat_id_uuid))
                    .one(db)
                    .await?;

                if let Some(user_state) = user_state {
                    let mut user_active: user_states::ActiveModel = user_state.into();
                    user_active.valid_messages = Set(user_active.valid_messages.unwrap() + 1);
                    user_active.update(db).await?;
                }
            }
        } else {
            tracing::info!(
                chat_id = chat_id,
                user_id = user_id,
                "AI checks enabled - message processed but not counted as valid"
            );
        }
    }

    Ok(())
}

fn detect_trigger_conditional(
    text: &str,
    entities: &[teloxide::types::MessageEntity],
    chat_data: &ChatData,
) -> Option<crate::bot::utils::Trigger> {
    use crate::bot::utils::Trigger;
    use teloxide::types::MessageEntityKind;

    // Check emoji overflow first
    if chat_data.cleanup_emojis {
        let emoji_count = crate::bot::utils::count_emojis(text);
        if emoji_count > chat_data.max_emoji_count as usize {
            return Some(Trigger::EmojiOverflow);
        }
    }

    // Entity-based detection with whitelist checks
    for e in entities {
        match e.kind {
            MessageEntityKind::Mention if chat_data.cleanup_mentions => {
                if let Some(mention) = crate::bot::utils::extract_mention_from_entity(text, e) {
                    tracing::info!(
                        "Found mention entity: '{}', allowed_mentions: {:?}",
                        mention,
                        chat_data.allowed_mentions
                    );
                    if let Some(ref allowed) = chat_data.allowed_mentions {
                        if allowed
                            .iter()
                            .any(|allowed_mention| allowed_mention.to_lowercase() == mention)
                        {
                            tracing::info!(
                                "Mention '{}' is whitelisted, skipping deletion",
                                mention
                            );
                            continue;
                        }
                    }
                    tracing::info!("Mention '{}' not whitelisted, triggering deletion", mention);
                    return Some(Trigger::MentionEntity);
                }
            }
            MessageEntityKind::Url | MessageEntityKind::TextLink { .. }
                if chat_data.cleanup_links =>
            {
                if let Some(url) = crate::bot::utils::extract_url_from_entity(text, e) {
                    if let Some(domain) = crate::bot::utils::normalize_domain(&url) {
                        if let Some(ref allowed) = chat_data.allowed_link_domains {
                            if allowed.contains(&domain) {
                                // Domain is whitelisted, skip deletion
                                continue;
                            }
                        }
                        return Some(match e.kind {
                            MessageEntityKind::Url => Trigger::LinkEntityUrl,
                            MessageEntityKind::TextLink { .. } => Trigger::LinkEntityTextLink,
                            _ => unreachable!(),
                        });
                    }
                }
            }
            _ => {}
        }
    }

    // Regex-based checks with whitelist validation
    if chat_data.cleanup_mentions {
        use crate::bot::utils::RE_MENTION;
        for captures in RE_MENTION.find_iter(text) {
            let mention_text = captures.as_str();
            // Extract username from the match, handling the regex pattern
            let mention = mention_text
                .split('@')
                .nth(1)
                .unwrap_or("")
                .split(|c: char| !c.is_alphanumeric() && c != '_')
                .next()
                .unwrap_or("")
                .to_lowercase();

            if !mention.is_empty() {
                tracing::info!(
                    "Found mention regex: '{}', allowed_mentions: {:?}",
                    mention,
                    chat_data.allowed_mentions
                );
                if let Some(ref allowed) = chat_data.allowed_mentions {
                    if allowed
                        .iter()
                        .any(|allowed_mention| allowed_mention.to_lowercase() == mention)
                    {
                        tracing::info!("Mention '{}' is whitelisted, skipping deletion", mention);
                        continue;
                    }
                }
                tracing::info!("Mention '{}' not whitelisted, triggering deletion", mention);
                return Some(Trigger::MentionRegex);
            }
        }
    }

    if chat_data.cleanup_emails {
        use crate::bot::utils::RE_EMAIL;
        if RE_EMAIL.is_match(text) {
            return Some(Trigger::EmailRegex);
        }
    }

    if chat_data.cleanup_links {
        use crate::bot::utils::RE_LINK_FALLBACK;
        for captures in RE_LINK_FALLBACK.find_iter(text) {
            let url_text = captures.as_str();
            if let Some(domain) = crate::bot::utils::normalize_domain(url_text) {
                if let Some(ref allowed) = chat_data.allowed_link_domains {
                    if allowed.contains(&domain) {
                        // Domain is whitelisted, continue checking other links
                        continue;
                    }
                }
                return Some(Trigger::LinkRegex);
            }
        }
    }

    None
}
