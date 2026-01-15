#!/bin/bash
# Log Platform Health Check Script
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

OPENSEARCH_URL="${OPENSEARCH_URL:-http://localhost:9200}"
INGEST_URL="${INGEST_URL:-http://localhost:8080}"
DASHBOARDS_URL="${DASHBOARDS_URL:-http://localhost:5601}"

pass() { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; FAILED=1; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }

FAILED=0

echo "═══════════════════════════════════════════════════════════"
echo "           LOG PLATFORM HEALTH CHECK"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 1. OpenSearch Cluster Health
echo "1. OpenSearch Cluster"
echo "───────────────────────────────────────────────────────────"
if STATUS=$(curl -sf "$OPENSEARCH_URL/_cluster/health" 2>/dev/null); then
    CLUSTER_STATUS=$(echo "$STATUS" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    NODES=$(echo "$STATUS" | grep -o '"number_of_nodes":[0-9]*' | cut -d':' -f2)
    if [ "$CLUSTER_STATUS" = "green" ]; then
        pass "Cluster status: $CLUSTER_STATUS ($NODES nodes)"
    elif [ "$CLUSTER_STATUS" = "yellow" ]; then
        warn "Cluster status: $CLUSTER_STATUS ($NODES nodes)"
    else
        fail "Cluster status: $CLUSTER_STATUS"
    fi
else
    fail "OpenSearch not reachable at $OPENSEARCH_URL"
fi
echo ""

# 2. Index Template
echo "2. Index Template"
echo "───────────────────────────────────────────────────────────"
if curl -sf "$OPENSEARCH_URL/_index_template/logs-template" >/dev/null 2>&1; then
    pass "logs-template exists"
else
    fail "logs-template missing"
fi
echo ""

# 3. ISM Policy
echo "3. ISM Retention Policy"
echo "───────────────────────────────────────────────────────────"
if curl -sf "$OPENSEARCH_URL/_plugins/_ism/policies/logs-retention" >/dev/null 2>&1; then
    pass "logs-retention policy exists"
else
    warn "logs-retention policy missing (optional)"
fi
echo ""

# 4. Ingestd Service
echo "4. Ingestd Service"
echo "───────────────────────────────────────────────────────────"
if HEALTH=$(curl -sf "$INGEST_URL/health" 2>/dev/null); then
    pass "Ingestd healthy: $HEALTH"
else
    fail "Ingestd not reachable at $INGEST_URL"
fi
echo ""

# 5. Test Ingestion
echo "5. Ingestion Test"
echo "───────────────────────────────────────────────────────────"
TEST_MSG="healthcheck-$(date +%s)"
if RESULT=$(curl -sf -X POST "$INGEST_URL/ingest" \
    -H "Content-Type: application/json" \
    -d "{\"service\":{\"name\":\"healthcheck\"},\"log\":{\"level\":\"info\"},\"message\":\"$TEST_MSG\"}" 2>/dev/null); then
    INDEXED=$(echo "$RESULT" | grep -o '"indexed":[0-9]*' | cut -d':' -f2)
    if [ "$INDEXED" = "1" ]; then
        pass "Ingested 1 document"
    else
        fail "Ingestion returned: $RESULT"
    fi
else
    fail "Ingestion failed"
fi
echo ""

# 6. Query Test
echo "6. Query Test"
echo "───────────────────────────────────────────────────────────"
sleep 1  # Wait for indexing
if COUNT=$(curl -sf "$OPENSEARCH_URL/logs-*/_count" 2>/dev/null | grep -o '"count":[0-9]*' | cut -d':' -f2); then
    if [ "$COUNT" -gt 0 ]; then
        pass "Found $COUNT documents in logs-* indices"
    else
        warn "No documents found yet"
    fi
else
    fail "Query failed"
fi
echo ""

# 7. Disk Usage
echo "7. Disk Usage (per node)"
echo "───────────────────────────────────────────────────────────"
if STATS=$(curl -sf "$OPENSEARCH_URL/_nodes/stats/fs" 2>/dev/null); then
    # Parse with basic tools
    TOTAL=$(echo "$STATS" | grep -o '"total_in_bytes":[0-9]*' | head -1 | cut -d':' -f2)
    FREE=$(echo "$STATS" | grep -o '"free_in_bytes":[0-9]*' | head -1 | cut -d':' -f2)
    if [ -n "$TOTAL" ] && [ -n "$FREE" ]; then
        USED=$((TOTAL - FREE))
        USED_GB=$((USED / 1073741824))
        TOTAL_GB=$((TOTAL / 1073741824))
        PCT=$((USED * 100 / TOTAL))
        if [ "$PCT" -lt 80 ]; then
            pass "Disk: ${USED_GB}GB / ${TOTAL_GB}GB (${PCT}%)"
        elif [ "$PCT" -lt 90 ]; then
            warn "Disk: ${USED_GB}GB / ${TOTAL_GB}GB (${PCT}%)"
        else
            fail "Disk: ${USED_GB}GB / ${TOTAL_GB}GB (${PCT}%) - CRITICAL"
        fi
    fi
else
    fail "Could not get disk stats"
fi
echo ""

# 8. Recent Indices
echo "8. Log Indices"
echo "───────────────────────────────────────────────────────────"
if INDICES=$(curl -sf "$OPENSEARCH_URL/_cat/indices/logs-*?h=index,docs.count,store.size&s=index:desc" 2>/dev/null); then
    if [ -n "$INDICES" ]; then
        echo "$INDICES" | head -5
        TOTAL_INDICES=$(echo "$INDICES" | wc -l | tr -d ' ')
        pass "Found $TOTAL_INDICES log indices"
    else
        warn "No log indices yet"
    fi
else
    warn "Could not list indices"
fi
echo ""

# 9. Dashboards
echo "9. OpenSearch Dashboards"
echo "───────────────────────────────────────────────────────────"
if curl -sf "$DASHBOARDS_URL/api/status" >/dev/null 2>&1; then
    pass "Dashboards reachable at $DASHBOARDS_URL"
else
    warn "Dashboards not reachable (may still be starting)"
fi
echo ""

# 10. Docker Containers (if docker available)
echo "10. Container Status"
echo "───────────────────────────────────────────────────────────"
if command -v docker &> /dev/null; then
    docker ps --filter "name=susbonk" --format "{{.Names}}\t{{.Status}}" 2>/dev/null | while read line; do
        NAME=$(echo "$line" | cut -f1)
        STATUS=$(echo "$line" | cut -f2)
        if echo "$STATUS" | grep -q "Up"; then
            if echo "$STATUS" | grep -q "healthy"; then
                pass "$NAME: $STATUS"
            else
                warn "$NAME: $STATUS"
            fi
        else
            fail "$NAME: $STATUS"
        fi
    done
else
    warn "Docker not available for container check"
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════"
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}All critical checks passed!${NC}"
else
    echo -e "${RED}Some checks failed. Review above.${NC}"
fi
echo ""
echo "Visual Check URLs:"
echo "  • Dashboards: $DASHBOARDS_URL"
echo "  • Discover:   $DASHBOARDS_URL/app/discover"
echo "  • Dev Tools:  $DASHBOARDS_URL/app/dev_tools"
echo "═══════════════════════════════════════════════════════════"

exit $FAILED
