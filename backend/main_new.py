from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from core.settings import settings
from core.db_helper import db_helper
from handlers import (
    auth_router,
    chat_router,
    prompt_router,
    user_state_router,
    deleted_messages_router,
    chat_prompt_links_router
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Starting up the SusBonk API...")
    yield
    print("Shutting down the SusBonk API...")
    await db_helper.dispose()

app = FastAPI(
    title="SusBonk Dashboard API",
    description="""
REST API for SusBonk spam detection dashboard.

## Features

* **Authentication**: JWT-based user authentication with Argon2 password hashing
* **System Prompts**: Read-only access to pre-configured spam detection prompts
* **Custom Prompts**: Full CRUD operations for user-created prompts
* **Chat Management**: View and configure chat settings for spam detection
* **User States**: Manage trusted users and moderation within chats
* **Deleted Messages**: View deleted messages from Redis streams
* **Chat-Prompt Linking**: Link prompts to chats with priority and threshold support

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
        },
        {
            "name": "deleted_messages",
            "description": "View deleted messages from Redis streams"
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
app.include_router(auth_router)
app.include_router(prompt_router)
app.include_router(chat_router)
app.include_router(user_state_router)
app.include_router(deleted_messages_router)
app.include_router(chat_prompt_links_router)

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring service availability"""
    return {
        "status": "healthy",
        "service": "susbonk-api",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting SusBonk API on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
