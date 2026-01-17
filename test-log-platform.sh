#!/bin/bash
# Test script for Log Platform and Email Delivery
# Run from: dynamous-kiro-hackathon/

set -e

echo "🧪 Log Platform & Email Test Suite"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Config
INGEST_URL="${OS_INGEST_URL:-http://localhost:8080/ingest}"
OS_URL="${OS_URL:-http://localhost:9200}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SERVICE_NAME="test-script"

echo "📋 Configuration:"
echo "   Ingest URL: $INGEST_URL"
echo "   OpenSearch URL: $OS_URL"
echo ""

# Test 1: OpenSearch Health
echo "🔍 Test 1: OpenSearch Health Check"
HEALTH=$(curl -s "$OS_URL/_cluster/health" 2>/dev/null || echo '{"status":"failed"}')
STATUS=$(echo "$HEALTH" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$STATUS" = "green" ] || [ "$STATUS" = "yellow" ]; then
    echo -e "   ${GREEN}✅ OpenSearch is $STATUS${NC}"
else
    echo -e "   ${RED}❌ OpenSearch health check failed: $STATUS${NC}"
fi
echo ""

# Test 2: Ingest Service Health
echo "🔍 Test 2: Ingest Service Health Check"
INGEST_HEALTH=$(curl -s "http://localhost:8080/health" 2>/dev/null || echo '{"status":"failed"}')
if echo "$INGEST_HEALTH" | grep -q '"status":"ok"'; then
    echo -e "   ${GREEN}✅ Ingest service is healthy${NC}"
else
    echo -e "   ${RED}❌ Ingest service health check failed${NC}"
fi
echo ""

# Test 3: Send a single log event
echo "🔍 Test 3: Sending Single Log Event"
SINGLE_LOG=$(cat <<EOF
{
  "@timestamp": "$TIMESTAMP",
  "service": {"name": "$SERVICE_NAME"},
  "log": {"level": "info"},
  "message": "Test log event from test-log-platform.sh",
  "fields": {"test_id": "single_event", "run_at": "$TIMESTAMP"}
}
EOF
)

RESPONSE=$(curl -s -X POST "$INGEST_URL" \
  -H "Content-Type: application/json" \
  -d "$SINGLE_LOG" 2>/dev/null || echo '{"error":"failed"}')

if echo "$RESPONSE" | grep -q '"indexed":1'; then
    echo -e "   ${GREEN}✅ Single log event indexed successfully${NC}"
else
    echo -e "   ${RED}❌ Failed to index single event: $RESPONSE${NC}"
fi
echo ""

# Test 4: Send batch log events (including WARN and ERROR)
echo "🔍 Test 4: Sending Batch Log Events (INFO, WARN, ERROR)"
BATCH_LOGS=$(cat <<EOF
[
  {"@timestamp": "$TIMESTAMP", "service": {"name": "$SERVICE_NAME"}, "log": {"level": "info"}, "message": "Batch test - info level"},
  {"@timestamp": "$TIMESTAMP", "service": {"name": "$SERVICE_NAME"}, "log": {"level": "warn"}, "message": "Batch test - warning level"},
  {"@timestamp": "$TIMESTAMP", "service": {"name": "$SERVICE_NAME"}, "log": {"level": "error"}, "message": "Batch test - error level (should trigger alert!)"}
]
EOF
)

RESPONSE=$(curl -s -X POST "$INGEST_URL" \
  -H "Content-Type: application/json" \
  -d "$BATCH_LOGS" 2>/dev/null || echo '{"error":"failed"}')

if echo "$RESPONSE" | grep -q '"indexed":3'; then
    echo -e "   ${GREEN}✅ Batch log events indexed successfully (3 events)${NC}"
else
    echo -e "   ${RED}❌ Failed to index batch: $RESPONSE${NC}"
fi
echo ""

# Test 5: Query recent logs
echo "🔍 Test 5: Querying Recent Logs from OpenSearch"
sleep 2  # Wait for indexing

QUERY=$(cat <<EOF
{
  "query": {
    "bool": {
      "must": [
        {"match": {"service.name": "$SERVICE_NAME"}}
      ]
    }
  },
  "size": 5,
  "sort": [{"@timestamp": "desc"}]
}
EOF
)

SEARCH_RESULT=$(curl -s -X POST "$OS_URL/logs-*/_search" \
  -H "Content-Type: application/json" \
  -d "$QUERY" 2>/dev/null)

HIT_COUNT=$(echo "$SEARCH_RESULT" | grep -o '"total":{"value":[0-9]*' | head -1 | grep -o '[0-9]*$')

if [ -n "$HIT_COUNT" ] && [ "$HIT_COUNT" -gt 0 ]; then
    echo -e "   ${GREEN}✅ Found $HIT_COUNT log events from test${NC}"
else
    echo -e "   ${YELLOW}⚠️ No logs found yet (may need more time to index)${NC}"
fi
echo ""

# Test 6: List all indices
echo "🔍 Test 6: Listing Log Indices"
INDICES=$(curl -s "$OS_URL/_cat/indices/logs-*?h=index,docs.count,store.size&s=index:desc" 2>/dev/null)
if [ -n "$INDICES" ]; then
    echo "   Log indices found:"
    echo "$INDICES" | while read line; do
        echo "   📁 $line"
    done
else
    echo -e "   ${YELLOW}⚠️ No log indices found${NC}"
fi
echo ""

# Summary
echo "==================================="
echo "🎯 Test Summary"
echo "==================================="
echo "Logs ingested at: $TIMESTAMP"
echo "Service name: $SERVICE_NAME"
echo ""
echo "📌 Next Steps:"
echo "   1. Check alertd logs: docker-compose logs alert-engine --tail 50"
echo "   2. View OpenSearch Dashboards: http://localhost:5601"
echo "   3. Check your inbox at susbonk@outlook.com for alert emails"
echo ""
echo "   To trigger error alert threshold (>1 error in 5 min),"
echo "   run this script again or send more error logs."
