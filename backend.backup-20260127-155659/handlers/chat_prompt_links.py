from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List
from uuid import UUID

from core.db_helper import db_helper
from core.security import get_current_user
from models import Chat, Prompt, CustomPrompt, ChatPrompts, ChatCustomPrompts, User
from schemas.chat_prompt_links import (
    ChatPromptLinkResponse, ChatPromptLinkCreate, ChatPromptLinksList,
    ChatCustomPromptLinkResponse, ChatCustomPromptLinkCreate, ChatCustomPromptLinksList
)

router = APIRouter(prefix="/chats", tags=["chat_prompt_links"])

# System Prompt Links
@router.get("/{chat_id}/prompt-links", response_model=ChatPromptLinksList)
async def get_chat_prompt_links(
    chat_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get system prompt links for a chat."""
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
    
    # Get prompt links
    result = await db.execute(
        select(ChatPrompts)
        .filter(ChatPrompts.chat_id == chat_id, ChatPrompts.is_active == True)
        .order_by(ChatPrompts.priority.asc().nulls_last())
        .offset(offset)
        .limit(limit)
    )
    links = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(ChatPrompts.id))
        .filter(ChatPrompts.chat_id == chat_id, ChatPrompts.is_active == True)
    )
    total = count_result.scalar()
    
    return ChatPromptLinksList(items=links, limit=limit, offset=offset, total=total)

@router.post("/{chat_id}/prompt-links", response_model=ChatPromptLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_prompt_link(
    chat_id: UUID,
    link_data: ChatPromptLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Create a system prompt link for a chat."""
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
    
    # Check prompt exists
    prompt_result = await db.execute(
        select(Prompt).filter(Prompt.id == link_data.prompt_id, Prompt.is_active == True)
    )
    prompt = prompt_result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    try:
        # Create link
        link = ChatPrompts(
            chat_id=chat_id,
            prompt_id=link_data.prompt_id,
            priority=link_data.priority
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prompt already linked to this chat"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prompt link"
        )

@router.delete("/{chat_id}/prompt-links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_prompt_link(
    chat_id: UUID,
    link_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Delete a system prompt link."""
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
    
    # Get link
    result = await db.execute(
        select(ChatPrompts).filter(
            ChatPrompts.id == link_id,
            ChatPrompts.chat_id == chat_id,
            ChatPrompts.is_active == True
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt link not found")
    
    try:
        link.is_active = False
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prompt link"
        )

# Custom Prompt Links
@router.get("/{chat_id}/custom-prompt-links", response_model=ChatCustomPromptLinksList)
async def get_chat_custom_prompt_links(
    chat_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get custom prompt links for a chat."""
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
    
    # Get custom prompt links
    result = await db.execute(
        select(ChatCustomPrompts)
        .filter(ChatCustomPrompts.chat_id == chat_id, ChatCustomPrompts.is_active == True)
        .order_by(ChatCustomPrompts.priority.asc().nulls_last())
        .offset(offset)
        .limit(limit)
    )
    links = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(ChatCustomPrompts.id))
        .filter(ChatCustomPrompts.chat_id == chat_id, ChatCustomPrompts.is_active == True)
    )
    total = count_result.scalar()
    
    return ChatCustomPromptLinksList(items=links, limit=limit, offset=offset, total=total)

@router.post("/{chat_id}/custom-prompt-links", response_model=ChatCustomPromptLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_custom_prompt_link(
    chat_id: UUID,
    link_data: ChatCustomPromptLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Create a custom prompt link for a chat."""
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
    
    # Check custom prompt exists and belongs to user
    prompt_result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.id == link_data.custom_prompt_id,
            CustomPrompt.user_id == current_user.id,
            CustomPrompt.is_active == True
        )
    )
    prompt = prompt_result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    try:
        # Create link
        link = ChatCustomPrompts(
            chat_id=chat_id,
            custom_prompt_id=link_data.custom_prompt_id,
            priority=link_data.priority
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Custom prompt already linked to this chat"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create custom prompt link"
        )

@router.delete("/{chat_id}/custom-prompt-links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_custom_prompt_link(
    chat_id: UUID,
    link_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Delete a custom prompt link."""
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
    
    # Get link
    result = await db.execute(
        select(ChatCustomPrompts).filter(
            ChatCustomPrompts.id == link_id,
            ChatCustomPrompts.chat_id == chat_id,
            ChatCustomPrompts.is_active == True
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt link not found")
    
    try:
        link.is_active = False
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete custom prompt link"
        )
