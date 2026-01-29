from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from core.db_helper import db_helper
from core.security import get_current_user
from models import Chat, UserState, User
from schemas.user_state import UserStateResponse, UserStateUpdate, UserStatesList

router = APIRouter(prefix="/chats", tags=["user_states"])

@router.get("/{chat_id}/user-states", response_model=UserStatesList)
async def get_user_states(
    chat_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get user states for a specific chat."""
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
    
    # Get user states
    result = await db.execute(
        select(UserState)
        .filter(UserState.chat_id == chat_id, UserState.is_active == True)
        .offset(offset)
        .limit(limit)
    )
    user_states = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(UserState.id))
        .filter(UserState.chat_id == chat_id, UserState.is_active == True)
    )
    total = count_result.scalar()
    
    return UserStatesList(
        items=user_states,
        limit=limit,
        offset=offset,
        total=total
    )

@router.patch("/{chat_id}/user-states/{state_id}", response_model=UserStateResponse)
async def update_user_state(
    chat_id: UUID,
    state_id: UUID,
    state_update: UserStateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Update a user state."""
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
    
    # Get user state
    result = await db.execute(
        select(UserState).filter(
            UserState.id == state_id,
            UserState.chat_id == chat_id,
            UserState.is_active == True
        )
    )
    user_state = result.scalar_one_or_none()
    if not user_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User state not found")
    
    try:
        update_data = state_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_state, field, value)
        
        await db.commit()
        await db.refresh(user_state)
        return user_state
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user state"
        )

@router.post("/{chat_id}/user-states/{state_id}/make-untrusted", response_model=UserStateResponse)
async def make_untrusted(
    chat_id: UUID,
    state_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Make a user untrusted."""
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
    
    # Get user state
    result = await db.execute(
        select(UserState).filter(
            UserState.id == state_id,
            UserState.chat_id == chat_id,
            UserState.is_active == True
        )
    )
    user_state = result.scalar_one_or_none()
    if not user_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User state not found")
    
    try:
        user_state.trusted = False
        await db.commit()
        await db.refresh(user_state)
        return user_state
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user state"
        )
