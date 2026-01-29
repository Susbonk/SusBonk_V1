from datetime import datetime, timezone

import requests

events = [
    {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),  # noqa: E501
        "service": {"name": "py-worker"},
        "log": {"level": "INFO"},
        "message": "step 1",
        "fields": {"job_id": 123, "step": 1},
    },
    {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),  # noqa: E501
        "service": {"name": "py-worker"},
        "log": {"level": "WARN"},
        "message": "step 2",
        "fields": {"job_id": 123, "step": 2},
    },
    {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),  # noqa: E501
        "service": {"name": "py-worker"},
        "log": {"level": "ERROR"},
        "message": "step 3",
        "fields": {"job_id": 123, "step": 3},
    },
    {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),  # noqa: E501
        "service": {"name": "py-worker"},
        "log": {"level": "ERROR"},
        "message": "step 4",
        "fields": {"job_id": 123, "step": 3},
    },
]

r = requests.post("http://localhost:8080/ingest", json=events, timeout=5)
print(r.status_code, r.text)
