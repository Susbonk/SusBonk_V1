# AI Service

Stateless LLM analysis service for SusBonk bot. Consumes messages from Redis streams, processes them through OpenRouter API, and returns raw LLM responses.

## Architecture

- **Stateless**: No database connections, pure processing service
- **Redis Streams**: Consumes from `ai:tasks`, publishes to `ai:results`
- **Worker Pool**: Configurable concurrent workers with rate limiting
- **OpenRouter API**: Flexible LLM provider access

## Configuration

Environment variables:

- `REDIS_URL` - Redis connection URL (default: `redis://localhost:6379`)
- `TASKS_STREAM` - Tasks stream name (default: `ai:tasks`)
- `RESULTS_STREAM` - Results stream name (default: `ai:results`)
- `CONSUMER_GROUP` - Consumer group name (default: `ai-workers`)
- `AI_BASE_URL` - LLM API base URL (default: `http://localhost:11434`)
- `AI_MODEL` - Model to use (default: `llama3`)
- `AI_API_KEY` - API key for OpenAI-compatible APIs (optional)
- `AI_WORKERS` - Number of concurrent workers (default: 4)
- `AI_TIMEOUT_S` - API timeout in seconds (default: 30)
- `AI_XREAD_COUNT` - Messages to read per batch (default: 5)
- `AI_RESULTS_MAXLEN` - Max results stream length (optional, uses MAXLEN ~)
- `OS_INGEST_URL` - OpenSearch ingest URL for structured logging (optional)
- `RUST_LOG` - Log level (default: `info`)

## Stream Format

### Input: `ai:tasks`

Redis stream fields:
- `job_id` - Unique job identifier (UUID)
- `payload` - Message text to analyze
- `extra_json` - JSON string containing prompts and metadata

Example:
```json
{
  "prompts": ["prompt1", "prompt2"],
  "chat_uuid": "uuid"
}
```

### Output: `ai:results`

Redis stream fields:
- `job_id` - Job identifier matching the input task
- `payload` - Raw LLM response string
- `extra_json` - JSON string containing success status and metadata

Example:
```json
{
  "success": true,
  "timestamp": 1234567890,
  "chat_uuid": "uuid"
}
```

## Running

### Local Development

```bash
export OPENROUTER_API_KEY=your_key_here
cargo run
```

### Docker

```bash
docker build -t ai-service .
docker run -e OPENROUTER_API_KEY=your_key ai-service
```

## Integration

The telegram bot is responsible for:
- Querying prompts from database
- Creating tasks with prompts included
- Consuming results and parsing responses
- Making moderation decisions

The ai-service only handles LLM API calls and returns raw responses.

## Testing

See [example_usage/](./example_usage/) for standalone testing scripts:

- `submit_task.py` - Submit a task to the AI service
- `tail_results.py` - Monitor the results stream
- `demo.py` - Submit a task and wait for the result

These scripts allow you to validate the AI service in isolation without running the full bot.

Example:
```bash
cd example_usage
pip install -r requirements.txt
python demo.py "Is this spam: Buy cheap watches now!"
```

See [example_usage/README.md](./example_usage/README.md) for detailed usage instructions.

## Dependency Management

This project uses `Cargo.lock` for deterministic builds:
- **Committed to git**: Yes, `Cargo.lock` is version controlled
- **Docker builds**: Use `cargo build --locked` to ensure exact versions
- **CI/CD**: Always use lockfile for reproducible builds
