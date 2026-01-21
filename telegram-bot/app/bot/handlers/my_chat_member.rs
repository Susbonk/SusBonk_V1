use crate::services;
use anyhow::Result;
use sea_orm::DatabaseConnection;
use teloxide::{
    Bot,
    prelude::Requester,
    types::{ChatMemberStatus, ChatMemberUpdated},
};

pub async fn handle_my_chat_member(
    bot: Bot,
    db: DatabaseConnection,
    upd: ChatMemberUpdated,
) -> Result<()> {
    // Only group/supergroup
    if !(upd.chat.is_group() || upd.chat.is_supergroup()) {
        return Ok(());
    }

    let chat_id = upd.chat.id;

    let old_s = upd.old_chat_member.status();
    let new_s = upd.new_chat_member.status();

    let added = matches!(
        new_s,
        ChatMemberStatus::Member | ChatMemberStatus::Administrator
    ) && matches!(old_s, ChatMemberStatus::Left | ChatMemberStatus::Banned);

    let removed = matches!(new_s, ChatMemberStatus::Left | ChatMemberStatus::Banned)
        && matches!(
            old_s,
            ChatMemberStatus::Member
                | ChatMemberStatus::Administrator
                | ChatMemberStatus::Restricted
        );

    if added {
        tracing::info!(%chat_id, "✅ bot added to chat");

        // Check if inviter exists in database
        let inviter_id = upd.from.id.0 as i64;

        match services::user_exists_by_telegram_id(&db, inviter_id).await {
            Ok(true) => {
                // User exists, add chat to database
                match services::add_chat(&db, &bot, &upd.chat, inviter_id).await {
                    Ok(()) => {
                        tracing::info!(%chat_id, inviter_id, "Chat added to database");
                    }
                    Err(e) => {
                        tracing::error!(%chat_id, inviter_id, error = %e, "Failed to add chat to database");
                    }
                }
            }
            Ok(false) => {
                // User doesn't exist, leave the chat
                tracing::warn!(%chat_id, inviter_id, "Inviter not in database, leaving chat");

                if let Err(e) = bot.leave_chat(chat_id).await {
                    tracing::error!(%chat_id, error = %e, "Failed to leave chat");
                }
            }
            Err(e) => {
                tracing::error!(%chat_id, inviter_id, error = %e, "Database error checking user");
            }
        }
    } else if removed {
        tracing::info!(%chat_id, old_status=?old_s, new_status=?new_s, "❌ bot removed from chat");
    } else if old_s != new_s {
        tracing::info!(%chat_id, old_status=?old_s, new_status=?new_s, "🔁 bot status changed");
    }

    Ok(())
}
