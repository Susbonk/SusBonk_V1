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
- `OPENROUTER_API_KEY` - OpenRouter API key (required)
- `OPENROUTER_MODEL` - Model to use (default: `openai/gpt-4o-mini`)
- `AI_WORKER_COUNT` - Number of concurrent workers (default: 4)
- `AI_RATE_LIMIT` - API calls per minute (default: 60)
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
