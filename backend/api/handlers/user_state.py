from typing import Optional
from datetime import datetime
from sqlalchemy import func, select
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from database.helper import get_db
from database.models import User, Chat, UserState
from database.schemas.chat import UserStateResponse, UserStateUpdate, UserStatesList
from api.deps.auth import get_current_user
from logger import logger

router = APIRouter(prefix="/chats", tags=["user_states"])


async def _ensure_chat_owned(db: AsyncSession, chat_id: UUID, current_user: User) -> None:
    """Verify chat ownership."""
    result = await db.execute(select(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
    ))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")


@router.get("/{chat_id}/user-states", response_model=UserStatesList)
async def list_chat_user_states(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    trusted: Optional[bool] = Query(None),
    external_user_id: Optional[int] = Query(None),
):
    """List user states for a chat."""
    # Verify ownership
    result = await db.execute(select(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
    ))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    query = select(UserState).filter(UserState.chat_id == chat_id)
    count_query = select(func.count()).select_from(UserState).filter(UserState.chat_id == chat_id)
    
    # Apply filters
    if trusted is not None:
        query = query.filter(UserState.trusted == trusted)
        count_query = count_query.filter(UserState.trusted == trusted)
    
    if external_user_id is not None:
        query = query.filter(UserState.external_user_id == external_user_id)
        count_query = count_query.filter(UserState.external_user_id == external_user_id)
    
    # Order and paginate
    query = query.order_by(UserState.updated_at.desc()).offset(offset).limit(limit)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    items_result = await db.execute(query)
    items = items_result.scalars().all()
    
    return UserStatesList(
        items=[UserStateResponse.model_validate(x) for x in items],
        limit=limit,
        offset=offset,
        total=total,
    )


@router.patch("/{chat_id}/user-states/{state_id}", response_model=UserStateResponse)
async def update_user_state(
    chat_id: UUID,
    state_id: UUID,
    payload: UserStateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a user state."""
    # Verify ownership
    result = await db.execute(select(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
    ))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    result = await db.execute(select(UserState).filter(
        UserState.id == state_id,
        UserState.chat_id == chat_id,
    ))
    user_state = result.scalar_one_or_none()
    if not user_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User state not found")
    
    try:
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(user_state, k, v)
        
        await db.commit()
        await db.refresh(user_state)
        
        logger.info(f"User state updated: {user_state.id}")
        return UserStateResponse.model_validate(user_state)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update user state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user state"
        )


@router.post("/{chat_id}/user-states/{state_id}/make-untrusted", response_model=UserStateResponse)
async def make_untrusted(
    chat_id: UUID,
    state_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset a user state to untrusted."""
    # Verify ownership
    result = await db.execute(select(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
    ))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    result = await db.execute(select(UserState).filter(
        UserState.id == state_id,
        UserState.chat_id == chat_id,
    ))
    user_state = result.scalar_one_or_none()
    if not user_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User state not found")
    
    try:
        user_state.trusted = False
        user_state.joined_at = datetime.utcnow()  # Reset joined_at
        user_state.valid_messages = 0
        
        await db.commit()
        await db.refresh(user_state)
        
        logger.info(f"User state reset to untrusted: {user_state.id}")
        return UserStateResponse.model_validate(user_state)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to reset user state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user state"
        )
