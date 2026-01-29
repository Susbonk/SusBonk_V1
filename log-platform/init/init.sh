#!/bin/sh
set -eu

OS="${OS_URL:-http://opensearch:9200}"

echo "[init] Waiting for OpenSearch..."
until curl -s "$OS" >/dev/null; do
  sleep 1
done
echo "[init] OpenSearch is up: $OS"

echo "[init] Apply ISM policy logs-default-ism..."
curl -s -X PUT "$OS/_plugins/_ism/policies/logs-default-ism" \
  -H "Content-Type: application/json" \
  --data-binary @/init/ism-policy.json >/dev/null
echo "[init] ISM policy applied"

echo "[init] Apply index template logs-default-template..."
curl -s -X PUT "$OS/_index_template/logs-default-template" \
  -H "Content-Type: application/json" \
  --data-binary @/init/index-template.json >/dev/null
echo "[init] Index template applied"

echo "[init] Done."
