from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from core.db_helper import db_helper
from core.security import get_current_user
from models import Chat, User
from schemas.chat import ChatResponse, ChatUpdate, ChatList

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("", response_model=ChatList)
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get all chats for the current user."""
    result = await db.execute(
        select(Chat).filter(Chat.user_id == current_user.id, Chat.is_active == True)
    )
    chats = result.scalars().all()
    return ChatList(chats=chats)

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get a specific chat by ID."""
    result = await db.execute(
        select(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id,
            Chat.is_active == True
        )
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    return chat

@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: UUID,
    chat_update: ChatUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Update chat settings."""
    result = await db.execute(
        select(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id,
            Chat.is_active == True
        )
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    try:
        # Update fields
        update_data = chat_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chat, field, value)
        
        await db.commit()
        await db.refresh(chat)
        return chat
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat"
        )
