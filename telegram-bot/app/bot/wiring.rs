use anyhow::Error;
use teloxide::{dptree, dispatching::UpdateHandler, prelude::*};
use sea_orm::DatabaseConnection;

use crate::bot::handlers::{self, GroupWorkItem};

pub fn make_handler() -> UpdateHandler<Error> {
    dptree::entry()
        // 1) Commands only in DM
        .branch(
            Update::filter_message()
                .filter(|msg: Message| msg.chat.is_private())
                .filter_command::<handlers::Command>()
                .endpoint(|bot: Bot, db: DatabaseConnection, msg: Message, cmd: handlers::Command| async move {
                    handlers::handle_command(bot, msg, cmd, &db).await
                }),
        )
        // 2) Only group/supergroup and text
        .branch(
            Update::filter_message()
                .filter(|msg: Message| msg.chat.is_group() || msg.chat.is_supergroup())
                .filter(|msg: Message| msg.text().is_some())
                .endpoint(|bot: Bot, db: DatabaseConnection, msg: Message, tx: tokio::sync::mpsc::Sender<GroupWorkItem>| async move {
                    handlers::handle_group_enqueue(bot, db, msg, tx).await
                }),
        )
        // 3) Only group/supergroup - now with database dependency
        .branch(
            Update::filter_my_chat_member()
                .endpoint(|bot: Bot, db: DatabaseConnection, upd: ChatMemberUpdated| async move {
                    handlers::handle_my_chat_member(bot, db, upd).await
                })
        )
}
