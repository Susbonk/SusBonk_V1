from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import settings
from api.handlers import auth, prompt, chat, user_state
from logger import logger

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
def health_check():
    """Health check endpoint for monitoring service availability"""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "susbonk-api"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting SusBonk API on {settings.api_host}:{settings.api_port}")
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
