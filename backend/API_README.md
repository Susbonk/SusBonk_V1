# SusBonk Dashboard API

FastAPI-based REST API backend for the SusBonk spam detection dashboard.

## Features

- **JWT Authentication**: Secure token-based authentication
- **System Prompts**: Read-only access to pre-configured spam detection prompts
- **Custom Prompts**: Full CRUD operations for user-created prompts
- **Chat Management**: View and configure chat settings
- **User State Management**: Manage trusted users and moderation

## Quick Start

### Development with Docker Compose

```bash
cd backend
docker-compose up -d api-backend
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Local Development

```bash
cd backend

# Install dependencies with uv
uv pip install -r pyproject.toml

# Run the server
python main.py
```

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile (requires auth)

### System Prompts (`/prompts`)
- `GET /prompts` - List system prompts (paginated, filterable)
- `GET /prompts/{id}` - Get single system prompt

### Custom Prompts (`/prompts/custom`)
- `GET /prompts/custom` - List user's custom prompts
- `GET /prompts/custom/{id}` - Get single custom prompt
- `POST /prompts/custom` - Create custom prompt
- `PATCH /prompts/custom/{id}` - Update custom prompt
- `DELETE /prompts/custom/{id}` - Delete custom prompt

### Chats (`/chats`)
- `GET /chats` - List user's chats
- `GET /chats/{id}` - Get chat settings
- `PATCH /chats/{id}` - Update chat settings

### User States (`/chats/{chat_id}/user-states`)
- `GET /chats/{chat_id}/user-states` - List chat members with pagination
- `PATCH /chats/{chat_id}/user-states/{state_id}` - Update trust status
- `POST /chats/{chat_id}/user-states/{state_id}/make-untrusted` - Reset user to untrusted

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

Include the JWT token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

## Environment Variables

Configure via `.env` file:

```env
# Database
POSTGRES_HOST=pg-database
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# JWT
JWT_SECRET=secret_string
JWT_ALG=HS256
JWT_ACCESS_TTL_MIN=10080

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── settings.py          # Configuration and environment variables
├── pyproject.toml       # Dependencies (uv)
├── Dockerfile           # Container image
├── api/
│   ├── security.py      # JWT and password utilities
│   ├── deps/
│   │   ├── auth.py      # Authentication dependency
│   │   └── ordering.py  # Query ordering helper
│   └── handlers/
│       ├── auth.py      # Authentication endpoints
│       ├── prompt.py    # Prompt endpoints
│       ├── chat.py      # Chat endpoints
│       └── user_state.py # User state endpoints
├── database/
│   ├── helper.py        # Database connection
│   ├── models/
│   │   └── models.py    # SQLAlchemy models
│   └── schemas/
│       ├── auth.py      # Auth Pydantic schemas
│       ├── prompt.py    # Prompt Pydantic schemas
│       └── chat.py      # Chat Pydantic schemas
└── logger/
    └── __init__.py      # Structured logging
```

## Development

### Adding New Endpoints

1. Create Pydantic schemas in `database/schemas/`
2. Create handler in `api/handlers/`
3. Register router in `main.py`

### Database Models

Models are defined in `database/models/models.py` and match the existing PostgreSQL schema.

### Logging

Structured JSON logging is configured in `logger/`. Use:

```python
from logger import logger
logger.info("Message")
logger.error("Error message")
```

## Production Considerations

- JWT tokens expire after 7 days (configurable via `JWT_ACCESS_TTL_MIN`)
- CORS is configured to allow all origins (restrict in production)
- Database connection pooling is enabled
- Health check endpoint at `/health` for monitoring
- Proper HTTP status codes (201, 204, 404, 409)
- Ownership validation ensures users can only access their own resources
