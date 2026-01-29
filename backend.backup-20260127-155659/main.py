from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from settings import settings
from api.handlers import auth, prompt, chat, user_state
from database.redis_helper import redis_helper
from logger import (
    setup_logging,
    start_log_shipping,
    stop_log_shipping,
    get_logger,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    await start_log_shipping()

    log.info("Starting up the SusBonk API...")
    
    # Test Redis connection
    try:
        redis_healthy = await redis_helper.health_check()
        if redis_healthy:
            log.info("Redis connection successful")
        else:
            log.warning("Redis connection failed - continuing without Redis")
    except Exception as e:
        log.warning(f"Redis connection error: {e} - continuing without Redis")

    yield

    log.info("Shutting down the SusBonk API...")
    await redis_helper.close()
    await stop_log_shipping()
    log.info("Application shutdown complete")


log = get_logger(__name__)


app = FastAPI(
    title="SusBonk Dashboard API",
    description="""
REST API for SusBonk spam detection dashboard.

## Features

* **Authentication**: JWT-based user authentication
* **System Prompts**: Read-only access to pre-configured spam detection prompts
* **Custom Prompts**: Full CRUD operations for user-created prompts
* **Chat Management**: View and configure chat settings for spam detection
* **User States**: Manage trusted users and moderation within chats

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.
Use the `Authorization: Bearer <token>` header with your JWT token.
    """,
    version="0.1.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    openapi_tags=[
        {
            "name": "auth",
            "description": "User authentication and registration"
        },
        {
            "name": "prompts",
            "description": "System prompts (read-only) and custom prompts (full CRUD)"
        },
        {
            "name": "chats",
            "description": "Chat configuration and settings management"
        },
        {
            "name": "user_states",
            "description": "User trust management and moderation within chats"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(prompt.router)
app.include_router(chat.router)
app.include_router(user_state.router)

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring service availability"""
    log.info("Health check requested")
    
    # Check database connection
    db_status = "disconnected"
    try:
        from database.helper import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
            db_status = "connected"
    except Exception as e:
        log.error(f"Database health check failed: {e}")
    
    # Check Redis connection
    redis_status = "connected" if await redis_helper.health_check() else "disconnected"
    
    return {
        "status": "healthy",
        "service": "susbonk-api",
        "database": db_status,
        "redis": redis_status
    }

if __name__ == "__main__":
    import uvicorn
    log.info(f"Starting SusBonk API on {settings.api_host}:{settings.api_port}")
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
