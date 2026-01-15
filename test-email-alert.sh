#!/bin/bash
# Test email alert sending via MailHog

source .env 2>/dev/null || true

SMTP_HOST=${SMTP_SERVER:-localhost}
SMTP_PORT_NUM=${SMTP_PORT:-1025}
TO_EMAIL=${ALERT_EMAIL_TO:-test@example.com}
FROM_EMAIL=${ALERT_EMAIL_FROM:-alerts@susbonk.local}

echo "📧 Testing Email Alert via MailHog"
echo "==================================="
echo "SMTP: $SMTP_HOST:$SMTP_PORT_NUM"
echo "From: $FROM_EMAIL"
echo "To: $TO_EMAIL"
echo ""

# Send test email
swaks --to "$TO_EMAIL" \
      --from "$FROM_EMAIL" \
      --server localhost \
      --port 1025 \
      --header "Subject: [TEST] SusBonk Alert - $(date +%H:%M:%S)" \
      --body "Test alert from SusBonk alertd service.

Timestamp: $(date)
Source: test-email-alert.sh

This email was captured by MailHog for testing."

echo ""
echo "✅ Email sent!"
echo ""
echo "📬 View captured emails at: http://localhost:8025"
echo ""
echo "To verify via API:"
echo "  curl -s http://localhost:8025/api/v2/messages | jq '.items[0].Content.Headers.Subject'"
