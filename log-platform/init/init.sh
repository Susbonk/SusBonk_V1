#!/bin/bash
set -e

OS_URL="${OPENSEARCH_URL:-http://opensearch:9200}"
OS_USER="${OPENSEARCH_USER:-admin}"
OS_PASS="${OPENSEARCH_PASSWORD:-Admin123!}"

echo "Waiting for OpenSearch at $OS_URL..."
until curl -k -u "$OS_USER:$OS_PASS" "$OS_URL/_cluster/health" &>/dev/null; do
  sleep 2
done
echo "OpenSearch ready"

echo "Applying ISM policy..."
curl -k -u "$OS_USER:$OS_PASS" -X PUT "$OS_URL/_plugins/_ism/policies/logs-retention" \
  -H "Content-Type: application/json" \
  -d @/init/ism-policy.json

echo "Applying index template..."
curl -k -u "$OS_USER:$OS_PASS" -X PUT "$OS_URL/_index_template/logs-template" \
  -H "Content-Type: application/json" \
  -d @/init/index-template.json

echo "OpenSearch initialization complete"
