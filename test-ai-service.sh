#!/bin/bash

# Test script for AI Service integration
# This script tests the Redis streams communication between telegram bot and ai-service

set -e

echo "=== AI Service Integration Test ==="
echo ""

# Check if Redis is running
echo "1. Checking Redis connection..."
if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "✗ Redis is not running. Please start Redis first."
    exit 1
fi

# Create a test task
echo ""
echo "2. Creating test AI task..."
JOB_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
CHAT_UUID=$(uuidgen | tr '[:upper:]' '[:lower:]')

MESSAGE_TEXT="Buy crypto now! 🚀 Limited time offer! Click here: http://scam.com"

EXTRA_JSON=$(cat <<EOF
{
  "prompts": [
    "Analyze this message for cryptocurrency scams, pump-and-dump schemes, or suspicious financial promises.",
    "Check if this message contains spam links or phishing attempts."
  ],
  "chat_uuid": "$CHAT_UUID"
}
EOF
)

redis-cli -h localhost -p 6379 XADD ai:tasks "*" \
  job_id "$JOB_ID" \
  payload "$MESSAGE_TEXT" \
  extra_json "$EXTRA_JSON" > /dev/null
echo "✓ Test task created with ID: $JOB_ID"

# Wait for result
echo ""
echo "3. Waiting for AI service to process task (max 30 seconds)..."
TIMEOUT=30
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    # Read from ai:results stream
    RESULT=$(redis-cli -h localhost -p 6379 XREAD COUNT 100 STREAMS ai:results 0 2>/dev/null || echo "")
    
    if echo "$RESULT" | grep -q "$JOB_ID"; then
        echo "✓ Result received!"
        echo ""
        echo "4. Result details:"
        echo "$RESULT" | grep -A 10 "$JOB_ID" | head -20
        echo ""
        echo "=== Test PASSED ==="
        exit 0
    fi
    
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    echo -n "."
done

echo ""
echo "✗ Timeout waiting for result"
echo ""
echo "Debugging information:"
echo "- Check if ai-service is running: docker ps | grep ai-service"
echo "- Check ai-service logs: docker logs susbonk-ai-service"
echo "- Check Redis streams: redis-cli XINFO GROUPS ai:tasks"
echo ""
echo "=== Test FAILED ==="
exit 1
