#!/bin/bash
set -e

echo "🐕 SusBonk Telegram Bot - Complete Validation Suite"
echo "===================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${BLUE}Running Core Functionality Tests...${NC}"
echo "---------------------------------------------------"
./test-e2e.sh
CORE_RESULT=$?

echo ""
echo ""
echo -e "${BLUE}Running Whitelist Feature Tests...${NC}"
echo "---------------------------------------------------"
./test-whitelist.sh
WHITELIST_RESULT=$?

echo ""
echo ""
echo "===================================================="
echo "📊 FINAL VALIDATION SUMMARY"
echo "===================================================="

if [ $CORE_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Core Functionality Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Core Functionality Tests: FAILED${NC}"
fi

if [ $WHITELIST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Whitelist Feature Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Whitelist Feature Tests: FAILED${NC}"
fi

echo ""

if [ $CORE_RESULT -eq 0 ] && [ $WHITELIST_RESULT -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                        ║${NC}"
    echo -e "${GREEN}║   🎉 ALL TESTS PASSED! 🎉             ║${NC}"
    echo -e "${GREEN}║                                        ║${NC}"
    echo -e "${GREEN}║   Status: PRODUCTION READY             ║${NC}"
    echo -e "${GREEN}║                                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "✅ Implemented Features:"
    echo "   • User auto-registration"
    echo "   • Chat auto-registration"
    echo "   • Spam detection with link analysis"
    echo "   • Automatic spam message deletion"
    echo "   • Database statistics tracking"
    echo "   • Whitelist management (add/remove/list)"
    echo "   • Admin permission enforcement"
    echo "   • Error handling improvements"
    echo "   • Input validation"
    echo "   • Cache management"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Set environment variables (TELEGRAM_BOT_TOKEN, DATABASE_URL, REDIS_URL)"
    echo "   2. Apply database schema: psql \$DATABASE_URL < ../backend/schema.sql"
    echo "   3. Start services: cd ../backend && docker-compose up -d"
    echo "   4. Deploy bot: docker-compose up telegram-bot"
    echo ""
    echo "📖 Documentation: See IMPLEMENTATION_COMPLETE.md"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                        ║${NC}"
    echo -e "${RED}║   ❌ SOME TESTS FAILED                 ║${NC}"
    echo -e "${RED}║                                        ║${NC}"
    echo -e "${RED}║   Status: NOT READY                    ║${NC}"
    echo -e "${RED}║                                        ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the test output above and fix the issues."
    echo ""
    exit 1
fi
