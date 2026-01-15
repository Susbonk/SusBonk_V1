#!/bin/bash
set -e

echo "📧 Postal Email Testing Script"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Postal is running
echo "🔍 Checking if Postal services are running..."
if ! docker ps | grep -q postal-smtp; then
    echo -e "${RED}❌ Postal SMTP server is not running${NC}"
    echo "Start it with: cd postal && docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}✅ Postal SMTP server is running${NC}"
echo ""

# Check if web UI is accessible
echo "🌐 Checking Postal web UI..."
if curl -sf http://localhost:5000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Postal web UI is accessible at http://localhost:5000${NC}"
else
    echo -e "${YELLOW}⚠️  Postal web UI may not be ready yet${NC}"
fi
echo ""

# Test SMTP connection
echo "🔌 Testing SMTP connection to postal-smtp:2525..."
if timeout 5 bash -c "</dev/tcp/localhost/2525" 2>/dev/null; then
    echo -e "${GREEN}✅ SMTP port 2525 is open${NC}"
else
    echo -e "${RED}❌ Cannot connect to SMTP port 2525${NC}"
    exit 1
fi
echo ""

# Run Rust integration test
echo "🧪 Running Rust integration test..."
echo "Command: cargo test --test email_integration -- --ignored"
echo ""
cd /Users/maximilianourik/Documents/REPO/Sus_bonk/dynamous-kiro-hackathon/log-platform
if cargo test --test email_integration -- --ignored 2>&1; then
    echo -e "${GREEN}✅ Integration test passed${NC}"
else
    echo -e "${RED}❌ Integration test failed${NC}"
    echo "Check the error messages above for details"
fi
echo ""

# Manual verification steps
echo "📋 Manual Verification Checklist:"
echo "================================"
echo ""
echo "1. Visit http://localhost:5000 to access Postal web UI"
echo "2. Log in with the admin credentials you created"
echo "3. Navigate to the Messages section"
echo "4. Look for test emails sent from alerts@postal.localhost"
echo "5. Verify the email content matches the test alert"
echo ""
echo "🔧 Troubleshooting:"
echo "==================="
echo ""
echo "If emails are not appearing:"
echo "  • Check Postal logs: docker-compose -f postal/docker-compose.yml logs postal-worker"
echo "  • Verify SMTP credentials in Postal web UI"
echo "  • Check that a mail server and domain are configured in Postal"
echo "  • Ensure the sending domain matches your Postal configuration"
echo ""
echo "If SMTP connection fails:"
echo "  • Verify Postal SMTP is running: docker ps | grep postal-smtp"
echo "  • Check network connectivity: docker network inspect susbonk-network"
echo "  • Review SMTP server logs: docker logs postal-smtp"
echo ""
echo "✅ Testing complete!"
