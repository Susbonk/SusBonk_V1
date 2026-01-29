#!/usr/bin/env python3
"""
Demo script: Submit a task and wait for the result.

Usage:
    python demo.py "Is this spam: Buy cheap watches now!"
    python demo.py "Check this message" --timeout 30
    REDIS_URL=redis://localhost:6379 python demo.py "Test message"
"""

import argparse
import os
import sys
import time
import uuid
import redis


def main():
    parser = argparse.ArgumentParser(description="Submit task and wait for result")
    parser.add_argument("payload", help="Message text to analyze")
    parser.add_argument("--timeout", type=int, default=60,
                        help="Timeout in seconds (default: 60)")
    parser.add_argument("--redis-url", default=os.getenv("REDIS_URL", "redis://localhost:6379"),
                        help="Redis URL (default: redis://localhost:6379)")
    parser.add_argument("--tasks-stream", default=os.getenv("TASKS_STREAM", "ai:tasks"),
                        help="Tasks stream name (default: ai:tasks)")
    parser.add_argument("--results-stream", default=os.getenv("RESULTS_STREAM", "ai:results"),
                        help="Results stream name (default: ai:results)")
    
    args = parser.parse_args()
    
    job_id = str(uuid.uuid4())
    
    try:
        r = redis.from_url(args.redis_url, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"Error: Cannot connect to Redis at {args.redis_url}", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Submit task
    print(f"Submitting task...")
    print(f"  Job ID: {job_id}")
    print(f"  Payload: {args.payload[:100]}{'...' if len(args.payload) > 100 else ''}")
    
    try:
        msg_id = r.xadd(args.tasks_stream, {
            "job_id": job_id,
            "payload": args.payload,
        })
        print(f"  Message ID: {msg_id}")
    except Exception as e:
        print(f"Error: Failed to submit task", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Wait for result
    print(f"\nWaiting for result (timeout: {args.timeout}s)...")
    
    start_time = time.time()
    last_id = "0-0"
    
    while time.time() - start_time < args.timeout:
        try:
            messages = r.xread({args.results_stream: last_id}, count=10, block=1000)
            
            if messages:
                for stream_name, stream_messages in messages:
                    for msg_id, fields in stream_messages:
                        last_id = msg_id
                        
                        if fields.get("job_id") == job_id:
                            # Found our result!
                            ok = fields.get("ok", "false") == "true"
                            elapsed = fields.get("elapsed_ms", "?")
                            
                            print(f"\n{'✓' if ok else '✗'} Result received!")
                            print(f"  Status: {'SUCCESS' if ok else 'FAILED'}")
                            print(f"  Elapsed: {elapsed}ms")
                            
                            if ok:
                                output = fields.get("output", "")
                                print(f"  Output: {output}")
                            else:
                                error = fields.get("error", "unknown error")
                                print(f"  Error: {error}")
                            
                            sys.exit(0 if ok else 1)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            sys.exit(130)
        except Exception as e:
            print(f"Error: Failed to read results", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"\nTimeout: No result received after {args.timeout}s")
    sys.exit(1)


if __name__ == "__main__":
    main()
