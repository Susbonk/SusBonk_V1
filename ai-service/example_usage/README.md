# AI Service Example Usage Scripts

Python scripts to test and validate the AI service in isolation using Redis streams.

## Prerequisites

```bash
pip install redis
```

Or using the project's Python environment:
```bash
cd ai-service/example_usage
pip install -r requirements.txt
```

## Scripts

### 1. `submit_task.py` - Submit a task to the AI service

Submit a message for spam analysis:

```bash
python submit_task.py "Is this spam: Buy cheap watches now!"
```

With custom job ID:
```bash
python submit_task.py "Check this message" --job-id custom-123
```

With custom Redis URL:
```bash
REDIS_URL=redis://localhost:6379 python submit_task.py "Test message"
```

**Options:**
- `--job-id`: Custom job ID (default: auto-generated UUID)
- `--redis-url`: Redis URL (default: `redis://localhost:6379`)
- `--stream`: Tasks stream name (default: `ai:tasks`)
- `--extra-json`: Optional JSON string for extra parameters

### 2. `tail_results.py` - Monitor results stream

Read last 10 results:
```bash
python tail_results.py
```

Follow mode (continuously read new results):
```bash
python tail_results.py --follow
```

Read last 20 results:
```bash
python tail_results.py --count 20
```

**Options:**
- `--redis-url`: Redis URL (default: `redis://localhost:6379`)
- `--stream`: Results stream name (default: `ai:results`)
- `--count`: Number of messages to read (default: 10)
- `--follow`, `-f`: Follow mode (continuously read new messages)

### 3. `demo.py` - Submit and wait for result

Submit a task and wait for the result:

```bash
python demo.py "Is this spam: Buy cheap watches now!"
```

With custom timeout:
```bash
python demo.py "Check this message" --timeout 30
```

**Options:**
- `--timeout`: Timeout in seconds (default: 60)
- `--redis-url`: Redis URL (default: `redis://localhost:6379`)
- `--tasks-stream`: Tasks stream name (default: `ai:tasks`)
- `--results-stream`: Results stream name (default: `ai:results`)

## Environment Variables

All scripts support these environment variables:

- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379`)
- `TASKS_STREAM`: Tasks stream name (default: `ai:tasks`)
- `RESULTS_STREAM`: Results stream name (default: `ai:results`)

Example:
```bash
export REDIS_URL=redis://redis-server:6379
export TASKS_STREAM=custom:tasks
export RESULTS_STREAM=custom:results

python demo.py "Test message"
```

## Testing the AI Service

### 1. Start Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Start the AI service
```bash
cd ai-service
cargo run
```

Or with Docker:
```bash
docker-compose up ai-service
```

### 3. Run the demo
```bash
cd ai-service/example_usage
python demo.py "Is this spam: Buy cheap watches now!"
```

Expected output:
```
Submitting task...
  Job ID: 12345678-1234-1234-1234-123456789abc
  Payload: Is this spam: Buy cheap watches now!
  Message ID: 1234567890123-0

Waiting for result (timeout: 60s)...

✓ Result received!
  Status: SUCCESS
  Elapsed: 1234ms
  Output: Yes, this appears to be spam...
```

## Troubleshooting

### Cannot connect to Redis
```
Error: Cannot connect to Redis at redis://localhost:6379
```

**Solution:** Ensure Redis is running:
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### No result received
```
Timeout: No result received after 60s
```

**Possible causes:**
1. AI service is not running
2. AI service cannot connect to Redis
3. AI model is not available
4. Task processing failed

**Check AI service logs:**
```bash
docker logs susbonk-ai-service
```

### Stream not found
If you get errors about missing streams, the AI service will create them automatically on first run.

## Stream Format

### Tasks Stream (`ai:tasks`)
```
job_id: <uuid>
payload: <message text>
extra_json: <optional JSON string>
```

### Results Stream (`ai:results`)
```
job_id: <uuid>
ok: true|false
elapsed_ms: <milliseconds>
output: <AI response> (if ok=true)
error: <error message> (if ok=false)
```
