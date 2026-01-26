from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from uuid import UUID
import redis.asyncio as redis
import json
from datetime import datetime

from core.db_helper import db_helper
from core.security import get_current_user
from core.settings import settings
from models import Chat, User
from schemas.deleted_messages import DeletedMessageResponse, DeletedMessagesList

router = APIRouter(prefix="/chats", tags=["deleted_messages"])

async def get_redis_client() -> redis.Redis:
    """Get Redis client connection."""
    if settings.REDIS_URL:
        return redis.from_url(settings.REDIS_URL, decode_responses=True)
    else:
        return redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )

@router.get("/{chat_id}/deleted-messages", response_model=DeletedMessagesList)
async def get_deleted_messages(
    chat_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get deleted messages for a specific chat from Redis streams."""
    # Check chat ownership
    chat_result = await db.execute(
        select(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id,
            Chat.is_active == True
        )
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    try:
        redis_client = await get_redis_client()
        
        # Read from Redis stream: deleted_messages:{chat_id}
        stream_key = f"deleted_messages:{chat_id}"
        
        # Get stream length for total count
        try:
            total = await redis_client.xlen(stream_key)
        except Exception:
            total = 0
        
        if total == 0:
            return DeletedMessagesList(items=[], limit=limit, offset=offset, total=0)
        
        # Read messages (newest first by reversing the range)
        try:
            # Get all messages and reverse for newest first
            messages = await redis_client.xrevrange(stream_key, count=limit, offset=offset)
        except Exception:
            messages = []
        
        # Parse messages and normalize platform_user_id
        items = []
        for message_id, fields in messages:
            try:
                # Normalize telegram_user_id to platform_user_id
                platform_user_id = fields.get('platform_user_id') or fields.get('telegram_user_id') or fields.get('user_id')
                
                item = DeletedMessageResponse(
                    message_id=fields.get('message_id', message_id),
                    chat_id=str(chat_id),
                    platform_user_id=str(platform_user_id) if platform_user_id else "unknown",
                    content=fields.get('content'),
                    timestamp=datetime.fromisoformat(fields.get('timestamp', datetime.utcnow().isoformat())),
                    reason=fields.get('reason'),
                    metadata=json.loads(fields.get('metadata', '{}')) if fields.get('metadata') else None
                )
                items.append(item)
            except Exception as e:
                # Skip malformed messages
                continue
        
        await redis_client.aclose()
        
        return DeletedMessagesList(
            items=items,
            limit=limit,
            offset=offset,
            total=total
        )
        
    except Exception as e:
        # Redis failure - return 502 Bad Gateway
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve deleted messages from Redis"
        )
