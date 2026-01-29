# Log Platform

Centralized logging services for SusBonk (OpenSearch ingest + alerting).

## Run (Docker Compose)

From repo root:

```bash
cp .env.example .env
# edit .env and replace CHANGE_ME_* values

docker compose up -d opensearch opensearch-dashboards opensearch-init log-ingest alertd
```

```sh
# Check init applied
curl -s http://localhost:9200/_index_template/logs-default-template?pretty
curl -s http://localhost:9200/_plugins/_ism/policies/logs-default-ism?pretty
```
