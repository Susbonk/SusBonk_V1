#!/usr/bin/env python3
"""
Tail the AI service results stream.

Usage:
    python tail_results.py
    python tail_results.py --follow
    REDIS_URL=redis://localhost:6379 python tail_results.py --count 10
"""

import argparse
import os
import sys
import time
import redis


def format_result(msg_id, fields):
    """Format a result message for display."""
    job_id = fields.get("job_id", "unknown")
    ok = fields.get("ok", "false") == "true"
    elapsed = fields.get("elapsed_ms", "?")
    
    status = "✓ SUCCESS" if ok else "✗ FAILED"
    
    print(f"\n{status} [{msg_id}]")
    print(f"  Job ID: {job_id}")
    print(f"  Elapsed: {elapsed}ms")
    
    if ok:
        output = fields.get("output", "")
        print(f"  Output: {output[:200]}{'...' if len(output) > 200 else ''}")
    else:
        error = fields.get("error", "unknown error")
        print(f"  Error: {error}")


def main():
    parser = argparse.ArgumentParser(description="Tail AI service results stream")
    parser.add_argument("--redis-url", default=os.getenv("REDIS_URL", "redis://localhost:6379"),
                        help="Redis URL (default: redis://localhost:6379)")
    parser.add_argument("--stream", default=os.getenv("RESULTS_STREAM", "ai:results"),
                        help="Results stream name (default: ai:results)")
    parser.add_argument("--count", type=int, default=10,
                        help="Number of messages to read (default: 10)")
    parser.add_argument("--follow", "-f", action="store_true",
                        help="Follow mode: continuously read new messages")
    
    args = parser.parse_args()
    
    try:
        r = redis.from_url(args.redis_url, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"Error: Cannot connect to Redis at {args.redis_url}", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Reading from stream: {args.stream}")
    
    if args.follow:
        print("Following mode (Ctrl+C to stop)...")
        last_id = "$"  # Start from new messages
        
        try:
            while True:
                messages = r.xread({args.stream: last_id}, count=args.count, block=1000)
                
                if messages:
                    for stream_name, stream_messages in messages:
                        for msg_id, fields in stream_messages:
                            format_result(msg_id, fields)
                            last_id = msg_id
        except KeyboardInterrupt:
            print("\n\nStopped.")
    else:
        # Read last N messages
        try:
            messages = r.xrevrange(args.stream, count=args.count)
            
            if not messages:
                print("No messages in stream.")
                return
            
            print(f"Last {len(messages)} message(s):\n")
            
            for msg_id, fields in reversed(messages):
                format_result(msg_id, fields)
        except Exception as e:
            print(f"Error: Failed to read from stream", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
