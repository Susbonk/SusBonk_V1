from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from database.helper import get_db
from database.models import User, Chat
from database.schemas.chat import ChatResponse, ChatUpdate, ChatList
from api.deps.auth import get_current_user
from logger import logger

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("", response_model=ChatList)
async def list_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),  # Added filter
    chat_type: Optional[str] = Query(None),  # Added filter
):
    """List all chats for the current user."""
    query = select(Chat).filter(Chat.user_id == current_user.id)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Chat.is_active == is_active)
    else:
        query = query.filter(Chat.is_active == True)
    
    if chat_type is not None:
        query = query.filter(Chat.type == chat_type)
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return ChatList(chats=[ChatResponse.model_validate(c) for c in items])

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat by ID."""
    result = await db.execute(
        select(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id,
        )
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return ChatResponse.model_validate(chat)

@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: UUID,
    chat_data: ChatUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update chat settings."""
    result = await db.execute(
        select(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id,
        )
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    try:
        update_data = chat_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chat, field, value)
        
        await db.commit()
        await db.refresh(chat)
        
        logger.info(f"Chat updated: {chat.id}")
        return ChatResponse.model_validate(chat)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat"
        )
