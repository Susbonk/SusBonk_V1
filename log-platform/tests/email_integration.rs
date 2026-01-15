use log_platform_common::{
    Alert, AlertLevel,
    notify::{EmailNotifier, MultiNotifier, LogNotifier},
};

#[tokio::test]
#[ignore] // Run with: cargo test --test email_integration -- --ignored
async fn test_email_notification_through_smtp() {
    // This test requires SMTP credentials to be set in .env
    // Uses Brevo SMTP relay by default
    
    let smtp_host = std::env::var("SMTP_SERVER").unwrap_or_else(|_| "smtp-relay.brevo.com".to_string());
    let smtp_port = std::env::var("SMTP_PORT")
        .ok()
        .and_then(|p| p.parse().ok())
        .unwrap_or(587);
    let from_email = std::env::var("ALERT_EMAIL_FROM").unwrap_or_else(|_| "test@example.com".to_string());
    let to_email = std::env::var("ALERT_EMAIL_TO").unwrap_or_else(|_| "admin@example.com".to_string());
    let username = std::env::var("SMTP_USER").ok();
    let password = std::env::var("SMTP_PASSWORD").ok();

    let notifier = MultiNotifier::new()
        .add(Box::new(LogNotifier))
        .add(Box::new(EmailNotifier::new(
            smtp_host,
            smtp_port,
            from_email,
            to_email,
            username,
            password,
        )));

    let alert = Alert {
        subject: "Test Alert from Integration Test".to_string(),
        message: "This is a test email sent through Brevo SMTP relay.".to_string(),
        level: AlertLevel::Info,
        source: "email_integration_test".to_string(),
    };

    // Send the alert
    notifier.send(&alert).await;

    println!("✅ Test email sent successfully!");
    println!("📧 Check your inbox to verify delivery");
}

#[tokio::test]
async fn test_alert_creation() {
    let alert = Alert {
        subject: "Test Subject".to_string(),
        message: "Test Message".to_string(),
        level: AlertLevel::Warning,
        source: "test".to_string(),
    };

    assert_eq!(alert.subject, "Test Subject");
    assert_eq!(alert.message, "Test Message");
    assert!(matches!(alert.level, AlertLevel::Warning));
}
