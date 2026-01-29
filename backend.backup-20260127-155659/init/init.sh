#!/bin/bash
set -e

OS_URL="${OS_URL:-http://localhost:9200}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Waiting for OpenSearch to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
  if curl -s "$OS_URL/_cluster/health" > /dev/null 2>&1; then
    echo "OpenSearch is ready!"
    break
  fi
  echo "Attempt $i/$MAX_RETRIES: OpenSearch not ready yet..."
  sleep $RETRY_INTERVAL
done

if ! curl -s "$OS_URL/_cluster/health" > /dev/null 2>&1; then
  echo "ERROR: OpenSearch failed to start after $MAX_RETRIES attempts"
  exit 1
fi

echo "Applying index template..."
curl -X PUT "$OS_URL/_index_template/logs-template" \
  -H "Content-Type: application/json" \
  -d @/init/index-template.json

echo "Applying ISM policy..."
curl -X PUT "$OS_URL/_plugins/_ism/policies/logs-retention" \
  -H "Content-Type: application/json" \
  -d @/init/ism-policy.json

echo "Initialization complete!"
