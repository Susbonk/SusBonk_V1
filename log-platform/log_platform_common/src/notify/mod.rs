use tracing::{info, error};
use lettre::{
    message::header::ContentType,
    transport::smtp::authentication::Credentials,
    AsyncSmtpTransport, AsyncTransport, Message, Tokio1Executor,
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Alert {
    pub subject: String,
    pub message: String,
    pub level: AlertLevel,
    pub source: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AlertLevel {
    Info,
    Warning,
    Error,
    Critical,
}

#[async_trait::async_trait]
pub trait Notifier: Send + Sync {
    async fn send(&self, alert: &Alert) -> anyhow::Result<()>;
}

pub struct LogNotifier;

#[async_trait::async_trait]
impl Notifier for LogNotifier {
    async fn send(&self, alert: &Alert) -> anyhow::Result<()> {
        info!("ALERT [{:?}] {}: {}", alert.level, alert.subject, alert.message);
        Ok(())
    }
}

pub struct EmailNotifier {
    smtp_host: String,
    smtp_port: u16,
    from_email: String,
    to_email: String,
    username: Option<String>,
    password: Option<String>,
}

impl EmailNotifier {
    pub fn new(smtp_host: String, smtp_port: u16, from_email: String, to_email: String, username: Option<String>, password: Option<String>) -> Self {
        Self {
            smtp_host,
            smtp_port,
            from_email,
            to_email,
            username,
            password,
        }
    }
}

#[async_trait::async_trait]
impl Notifier for EmailNotifier {
    async fn send(&self, alert: &Alert) -> anyhow::Result<()> {
        let email = Message::builder()
            .from(self.from_email.parse()?)
            .to(self.to_email.parse()?)
            .subject(&alert.subject)
            .header(ContentType::TEXT_PLAIN)
            .body(format!("[{:?}] {}\n\nSource: {}", alert.level, alert.message, alert.source))?;

        let mut mailer_builder = AsyncSmtpTransport::<Tokio1Executor>::relay(&self.smtp_host)?
            .port(self.smtp_port);

        if let (Some(user), Some(pass)) = (&self.username, &self.password) {
            mailer_builder = mailer_builder.credentials(Credentials::new(user.clone(), pass.clone()));
        }

        let mailer = mailer_builder.build();
        mailer.send(email).await?;
        info!("Email sent to {}: {}", self.to_email, alert.subject);
        Ok(())
    }
}

pub struct MultiNotifier {
    notifiers: Vec<Box<dyn Notifier>>,
}

impl MultiNotifier {
    pub fn new() -> Self {
        Self { notifiers: Vec::new() }
    }

    pub fn add(mut self, notifier: Box<dyn Notifier>) -> Self {
        self.notifiers.push(notifier);
        self
    }

    pub async fn send(&self, alert: &Alert) {
        for notifier in &self.notifiers {
            if let Err(e) = notifier.send(alert).await {
                error!("Notification failed: {}", e);
            }
        }
    }

    pub async fn send_simple(&self, subject: &str, message: &str, level: AlertLevel) {
        self.send(&Alert {
            subject: subject.to_string(),
            message: message.to_string(),
            level,
            source: "alertd".to_string(),
        }).await;
    }
}

impl Default for MultiNotifier {
    fn default() -> Self {
        Self::new()
    }
}
