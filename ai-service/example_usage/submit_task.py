#!/usr/bin/env python3
"""
Submit a task to the AI service via Redis stream.

Usage:
    python submit_task.py "Is this spam: Buy cheap watches now!"
    python submit_task.py "Check this message" --job-id custom-123
    REDIS_URL=redis://localhost:6379 python submit_task.py "Test message"
"""

import argparse
import os
import sys
import uuid
import redis


def main():
    parser = argparse.ArgumentParser(description="Submit task to AI service")
    parser.add_argument("payload", help="Message text to analyze")
    parser.add_argument("--job-id", help="Custom job ID (default: auto-generated UUID)")
    parser.add_argument("--redis-url", default=os.getenv("REDIS_URL", "redis://localhost:6379"),
                        help="Redis URL (default: redis://localhost:6379)")
    parser.add_argument("--stream", default=os.getenv("TASKS_STREAM", "ai:tasks"),
                        help="Tasks stream name (default: ai:tasks)")
    parser.add_argument("--extra-json", help="Optional JSON string for extra parameters")
    
    args = parser.parse_args()
    
    job_id = args.job_id or str(uuid.uuid4())
    
    try:
        r = redis.from_url(args.redis_url, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"Error: Cannot connect to Redis at {args.redis_url}", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    
    fields = {
        "job_id": job_id,
        "payload": args.payload,
    }
    
    if args.extra_json:
        fields["extra_json"] = args.extra_json
    
    try:
        msg_id = r.xadd(args.stream, fields)
        print(f"✓ Task submitted successfully")
        print(f"  Job ID: {job_id}")
        print(f"  Message ID: {msg_id}")
        print(f"  Stream: {args.stream}")
    except Exception as e:
        print(f"Error: Failed to submit task", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
