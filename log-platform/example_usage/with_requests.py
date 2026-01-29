#!/usr/bin/env python3
"""Send test INFO logs to ingestd using Python requests"""

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
    send_log("INFO", "Application started")
    send_log("INFO", "Processing request", trace_id="req-001")
    send_log("INFO", "Request completed successfully")
