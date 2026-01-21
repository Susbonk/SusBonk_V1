use chrono::Utc;
use entity::{chats, user_states, users};
use sea_orm::{ActiveModelTrait, ColumnTrait, DatabaseConnection, EntityTrait, QueryFilter, Set};
use uuid::Uuid;
use teloxide::{Bot, prelude::Requester};

pub async fn user_exists_by_telegram_id(
    db: &DatabaseConnection,
    telegram_id: i64,
) -> Result<bool, sea_orm::DbErr> {
    let user = users::Entity::find()
        .filter(users::Column::TelegramUserId.eq(telegram_id))
        .filter(users::Column::IsActive.eq(true))
        .one(db)
        .await?;

    Ok(user.is_some())
}

async fn get_chat_invite_link(bot: &Bot, chat_id: teloxide::types::ChatId) -> Option<String> {
    match bot.export_chat_invite_link(chat_id).await {
        Ok(link) => Some(link),
        Err(_) => {
            tracing::info!("Failed to get invite link for chat {}", chat_id);
            None
        },
    }
}

pub async fn add_chat(
    db: &DatabaseConnection,
    bot: &Bot,
    chat: &teloxide::types::Chat,
    inviter_telegram_id: i64,
) -> Result<(), sea_orm::DbErr> {
    // Check if chat already exists
    let existing_chat = chats::Entity::find()
        .filter(chats::Column::PlatformChatId.eq(chat.id.0))
        .one(db)
        .await?;

    if existing_chat.is_some() {
        return Ok(()); // Chat already exists, nothing to do
    }

    let user = users::Entity::find()
        .filter(users::Column::TelegramUserId.eq(inviter_telegram_id))
        .filter(users::Column::IsActive.eq(true))
        .one(db)
        .await?
        .ok_or_else(|| sea_orm::DbErr::Custom("User not found".to_string()))?;

    let chat_link = get_chat_invite_link(bot, chat.id).await;

    let chat_model = chats::ActiveModel {
        id: Set(Uuid::new_v4()),
        created_at: Set(Utc::now().into()),
        updated_at: Set(Utc::now().into()),
        is_active: Set(true),
        r#type: Set("telegram".to_string()),
        platform_chat_id: Set(chat.id.0),
        title: Set(chat.title().map(|s| s.to_string())),
        chat_link: Set(chat_link),
        enable_ai_check: Set(true),

        // TODO: Move out to config (default chat thresholds)
        prompts_threshold: Set(0.3),
        custom_prompt_threshold: Set(0.3),

        cleanup_mentions: Set(false),
        cleanup_emojis: Set(false),
        cleanup_links: Set(false),
        allowed_link_domains: Set(None),
        user_id: Set(user.id),
        messages_deleted: Set(0),
        processed_messages: Set(0),
        spam_detected: Set(0),
        allowed_mentions: Set(None),
        cleanup_emails: Set(false),

        // TODO: Move out to config (default emoji max count)
        max_emoji_count: Set(5),
    };

    chat_model.insert(db).await?;
    Ok(())
}

pub async fn ensure_user_state(
    db: &DatabaseConnection,
    telegram_user_id: i64,
    chat_id: i64,
) -> Result<(), sea_orm::DbErr> {
    // Find the chat first
    let chat = chats::Entity::find()
        .filter(chats::Column::PlatformChatId.eq(chat_id))
        .one(db)
        .await?
        .ok_or_else(|| sea_orm::DbErr::Custom("Chat not found".to_string()))?;

    // Check if user state already exists
    let existing_state = user_states::Entity::find()
        .filter(user_states::Column::ExternalUserId.eq(telegram_user_id))
        .filter(user_states::Column::ChatId.eq(chat.id))
        .one(db)
        .await?;

    if existing_state.is_none() {
        let user_state = user_states::ActiveModel {
            id: Set(Uuid::new_v4()),
            created_at: Set(Utc::now().into()),
            updated_at: Set(Utc::now().into()),
            is_active: Set(true),
            external_user_id: Set(telegram_user_id),
            trusted: Set(false),
            joined_at: Set(Some(Utc::now().into())),
            valid_messages: Set(0),
            chat_id: Set(chat.id),
        };

        user_state.insert(db).await?;
    }

    Ok(())
}

pub async fn is_user_trusted(
    db: &DatabaseConnection,
    telegram_user_id: i64,
    chat_id: i64,
) -> Result<bool, sea_orm::DbErr> {
    let chat = chats::Entity::find()
        .filter(chats::Column::PlatformChatId.eq(chat_id))
        .one(db)
        .await?
        .ok_or_else(|| sea_orm::DbErr::Custom("Chat not found".to_string()))?;

    let user_state = user_states::Entity::find()
        .filter(user_states::Column::ExternalUserId.eq(telegram_user_id))
        .filter(user_states::Column::ChatId.eq(chat.id))
        .filter(user_states::Column::IsActive.eq(true))
        .one(db)
        .await?;

    Ok(user_state.map(|state| state.trusted).unwrap_or(false))
}

pub async fn is_chat_owner(
    db: &DatabaseConnection,
    telegram_user_id: i64,
    chat_id: i64,
) -> Result<bool, sea_orm::DbErr> {
    let user = users::Entity::find()
        .filter(users::Column::TelegramUserId.eq(telegram_user_id))
        .one(db)
        .await?;

    if let Some(user) = user {
        let chat = chats::Entity::find()
            .filter(chats::Column::PlatformChatId.eq(chat_id))
            .filter(chats::Column::UserId.eq(user.id))
            .one(db)
            .await?;

        Ok(chat.is_some())
    } else {
        Ok(false)
    }
}

#[derive(Debug)]
pub enum ConnectionResult {
    Success,
    AlreadyConnectedToSameAccount,
    AlreadyConnectedToOtherAccount,
    UserNotFound,
}

pub async fn update_chat_link_if_empty(
    db: &DatabaseConnection,
    bot: &Bot,
    chat_id: i64,
) -> Result<(), sea_orm::DbErr> {
    let chat = chats::Entity::find()
        .filter(chats::Column::PlatformChatId.eq(chat_id))
        .filter(
            chats::Column::ChatLink.is_null()
                .or(chats::Column::ChatLink.eq(""))
        )
        .one(db)
        .await?;

    if let Some(chat) = chat {
        if let Some(invite_link) = get_chat_invite_link(bot, teloxide::types::ChatId(chat_id)).await {
            let mut chat: chats::ActiveModel = chat.into();
            chat.chat_link = Set(Some(invite_link));
            chat.updated_at = Set(Utc::now().into());
            chat.update(db).await?;
        }
    }

    Ok(())
}

pub async fn connect_telegram_to_account(
    db: &DatabaseConnection,
    user_uuid: Uuid,
    telegram_user_id: i64,
) -> Result<ConnectionResult, sea_orm::DbErr> {
    // Check if telegram_user_id is already connected to any account
    let existing_user = users::Entity::find()
        .filter(users::Column::TelegramUserId.eq(telegram_user_id))
        .one(db)
        .await?;

    if let Some(existing_user) = existing_user {
        if existing_user.id == user_uuid {
            return Ok(ConnectionResult::AlreadyConnectedToSameAccount);
        } else {
            return Ok(ConnectionResult::AlreadyConnectedToOtherAccount);
        }
    }

    // Find user by UUID and update telegram_user_id
    let user = users::Entity::find_by_id(user_uuid)
        .one(db)
        .await?;

    if let Some(user) = user {
        let mut user: users::ActiveModel = user.into();
        user.telegram_user_id = Set(Some(telegram_user_id));
        user.updated_at = Set(Utc::now().into());
        user.update(db).await?;
        Ok(ConnectionResult::Success)
    } else {
        Ok(ConnectionResult::UserNotFound)
    }
}
