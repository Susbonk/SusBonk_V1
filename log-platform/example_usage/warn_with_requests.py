from datetime import datetime, timezone

import requests

events = [
    {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),  # noqa: E501
        "service": {"name": "py-worker"},
        "log": {"level": "WARN"},
        "message": "Warning from python",
        "fields": {"job_id": 123, "step": 3},
    },
]

r = requests.post("http://localhost:8080/ingest", json=events, timeout=5)
print(r.status_code, r.text)
