use log_platform_domain::Alert;
use serde::{Deserialize, Serialize};
use std::env;

use lettre::message::Mailbox;
use lettre::transport::smtp::authentication::{Credentials, Mechanism};
use lettre::{Message, SmtpTransport, Transport};

use tracing::{error, info, warn};

/// Trait for different notification mechanisms
pub trait Notifier: Send + Sync {
    fn notify(&self, alert: Alert);
}

/// A notifier that prints alerts to stdout
pub struct StdoutNotifier;

impl Notifier for StdoutNotifier {
    fn notify(&self, alert: Alert) {
        println!("[{}][{}] {}", alert.severity, alert.kind, alert.message);
    }
}

/// A notifier that sends alert emails
#[derive(Clone)]
pub struct EmailNotifier {
    pub cfg: EmailCfg,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct EmailCfg {
    pub enabled: bool,
    pub smtp_server: String,
    pub smtp_port: u16,
    pub smtp_user: String,
    pub smtp_password: String,
    pub to_list: Vec<String>,
    pub from: String,
}

impl EmailNotifier {
    pub fn new(cfg: EmailCfg) -> Self {
        Self { cfg }
    }

    pub fn from_env() -> Result<Self, anyhow::Error> {
        let to_raw = env::var("ALERT_EMAIL_TO").unwrap_or_default();
        let to_list = crate::parse::parse_email_list(&to_raw);

        let from = env::var("ALERT_EMAIL_FROM")
            .ok()
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .unwrap_or_else(|| env::var("SMTP_USER").unwrap_or_default());

        let email_cfg = EmailCfg {
            enabled: crate::env::env_bool("EMAIL_ENABLED", false),
            smtp_server: env::var("SMTP_SERVER").unwrap_or_default(),
            smtp_port: crate::env::env_parse("SMTP_PORT", 587u16),
            smtp_user: env::var("SMTP_USER").unwrap_or_default(),
            smtp_password: env::var("SMTP_PASSWORD").unwrap_or_default(),
            to_list,
            from,
        };

        if email_cfg.enabled {
            if email_cfg.smtp_server.is_empty()
                || email_cfg.smtp_user.is_empty()
                || email_cfg.smtp_password.is_empty()
                || email_cfg.to_list.is_empty()
            {
                return Err(anyhow::anyhow!(
                    "EMAIL_ENABLED=1 but SMTP/EMAIL env vars are incomplete"
                ));
            }
        }

        Ok(Self::new(email_cfg))
    }

    fn send_sync(&self, subject: &str, body: &str) -> anyhow::Result<()> {
        let from: Mailbox = self.cfg.from.parse()?;

        let creds = Credentials::new(self.cfg.smtp_user.clone(), self.cfg.smtp_password.clone());

        let mailer = if self.cfg.smtp_port == 465 {
            use lettre::transport::smtp::client::{Tls, TlsParameters};
            let tls_parameters = TlsParameters::new(self.cfg.smtp_server.clone())?;
            SmtpTransport::builder_dangerous(&self.cfg.smtp_server)
                .port(self.cfg.smtp_port)
                .tls(Tls::Wrapper(tls_parameters))
                .credentials(creds)
                .authentication(vec![Mechanism::Login])
                .build()
        } else {
            SmtpTransport::relay(&self.cfg.smtp_server)?
                .port(self.cfg.smtp_port)
                .credentials(creds)
                .authentication(vec![Mechanism::Login])
                .build()
        };

        if self.cfg.to_list.is_empty() {
            anyhow::bail!("no recipients in ALERT_EMAIL_TO");
        }

        let mut ok = 0usize;
        let mut fail = 0usize;
        let mut last_err: Option<anyhow::Error> = None;

        for to_s in &self.cfg.to_list {
            let to: Mailbox = match to_s.parse() {
                Ok(v) => v,
                Err(e) => {
                    fail += 1;
                    last_err = Some(e.into());
                    continue;
                }
            };

            let email = Message::builder()
                .from(from.clone())
                .to(to)
                .subject(subject)
                .body(body.to_string())?;

            match mailer.send(&email) {
                Ok(_) => ok += 1,
                Err(e) => {
                    fail += 1;
                    last_err = Some(e.into());
                }
            }
        }

        if ok == 0 {
            return Err(
                last_err.unwrap_or_else(|| anyhow::anyhow!("failed to send to all recipients"))
            );
        }

        if fail > 0 {
            warn!("email partially sent: ok={}, fail={}", ok, fail);
        }

        Ok(())
    }
}

impl Notifier for EmailNotifier {
    fn notify(&self, alert: Alert) {
        if !self.cfg.enabled {
            warn!("email notification disabled");
            return;
        }

        let subject = format!("[{}][{}] OpenSearch Alert", alert.severity, alert.kind);
        let body = alert.message.clone();
        let me = self.clone();

        // IMPORTANT: do not block alert loop
        tokio::task::spawn_blocking(move || {
            info!("attempting to send alert email: {}", subject);
            info!(
                "SMTP server: {}, port: {}, user: {}",
                me.cfg.smtp_server, me.cfg.smtp_port, me.cfg.smtp_user
            );

            match me.send_sync(&subject, &body) {
                Ok(_) => info!("email sent successfully"),
                Err(e) => error!("email send failed: {e}"),
            }
        });
    }
}

/// A notifier that combines multiple notifiers
pub struct MultiNotifier {
    pub sinks: Vec<Box<dyn Notifier>>,
}

impl MultiNotifier {
    pub fn new(sinks: Vec<Box<dyn Notifier>>) -> Self {
        Self { sinks }
    }
}

impl Notifier for MultiNotifier {
    fn notify(&self, alert: Alert) {
        for s in &self.sinks {
            s.notify(alert.clone());
        }
    }
}
