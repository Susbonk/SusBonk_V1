use sea_orm::{Database, DatabaseConnection, DbErr};
use config::CONFIG;

pub async fn connect() -> Result<DatabaseConnection, DbErr> {
    Database::connect(&CONFIG.database.to_url()).await
}
