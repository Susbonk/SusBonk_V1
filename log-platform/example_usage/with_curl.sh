#!/bin/bash
# Send test logs to ingestd using curl

INGEST_URL="${INGEST_URL:-http://localhost:8080/ingest}"

echo "Sending INFO log..."
curl -X POST "$INGEST_URL" \
  -H "Content-Type: application/json" \
  -d '[{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "service": {"name": "test-service"},
    "log": {"level": "INFO"},
    "message": "Test info message from curl"
  }]'

echo -e "\n\nSending WARN log..."
curl -X POST "$INGEST_URL" \
  -H "Content-Type: application/json" \
  -d '[{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "service": {"name": "test-service"},
    "log": {"level": "WARN"},
    "message": "Test warning message from curl"
  }]'

echo -e "\n\nSending ERROR log..."
curl -X POST "$INGEST_URL" \
  -H "Content-Type: application/json" \
  -d '[{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "service": {"name": "test-service"},
    "log": {"level": "ERROR"},
    "message": "Test error message from curl",
    "trace": {"id": "test-trace-123"}
  }]'

echo -e "\n\nDone!"
