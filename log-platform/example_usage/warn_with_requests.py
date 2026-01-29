#!/usr/bin/env python3
"""Send test WARN/ERROR logs to ingestd using Python requests"""

import requests
from datetime import datetime, timezone

INGEST_URL = "http://localhost:8080/ingest"

def send_log(level: str, message: str, trace_id: str = None):
    log_event = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "service": {"name": "python-test"},
        "log": {"level": level},
        "message": message
    }
    if trace_id:
        log_event["trace"] = {"id": trace_id}
    
    response = requests.post(INGEST_URL, json=[log_event])
    print(f"[{level}] {message} -> {response.status_code}")

if __name__ == "__main__":
    send_log("WARN", "High memory usage detected")
    send_log("ERROR", "Database connection failed", trace_id="err-001")
    send_log("ERROR", "Failed to process message", trace_id="err-002")
