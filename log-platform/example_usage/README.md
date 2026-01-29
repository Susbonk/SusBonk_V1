# Example Usage Scripts

Scripts to manually test log ingestion and alerting behavior.

## Prerequisites

- Ingestd service running on `http://localhost:8080`
- Python 3 with `requests` library (for Python scripts)

## Scripts

### `with_curl.sh`
Send INFO, WARN, and ERROR logs using curl.

```bash
./with_curl.sh
```

### `with_requests.py`
Send INFO logs using Python requests.

```bash
python3 with_requests.py
```

### `warn_with_requests.py`
Send WARN and ERROR logs using Python requests.

```bash
python3 warn_with_requests.py
```

## Verify Logs

Query OpenSearch to see indexed logs:

```bash
curl -k -u admin:Admin123! "http://localhost:9200/logs-*/_search?size=10&sort=@timestamp:desc"
```

Or view in OpenSearch Dashboards at `http://localhost:5601`
