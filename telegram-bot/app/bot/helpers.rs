use anyhow::Result;
use teloxide::{prelude::Requester, Bot};
use teloxide::types::{ChatId, MessageId};

pub async fn delete_message_by_ids(bot: &Bot, chat_id: ChatId, message_id: MessageId) -> Result<()> {
    bot.delete_message(chat_id, message_id).await?;
    Ok(())
}
