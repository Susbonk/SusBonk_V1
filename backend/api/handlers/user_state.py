from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from database.helper import get_db
from database.models import User, Chat, UserState
from database.schemas.chat import UserStateResponse, UserStateUpdate, UserStatesList
from api.deps.auth import get_current_user
from api.deps.ordering import Ordering
from logger import logger

router = APIRouter(prefix="/chats/{chat_id}/user-states", tags=["user_states"])

def verify_chat_ownership(chat_id: UUID, current_user: User, db: Session) -> Chat:
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
        Chat.is_active == True
    ).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat

@router.get("", response_model=UserStatesList)
def list_user_states(
    chat_id: UUID,
    limit: int = Query(50, ge=1, le=200),  # Senior uses limit/offset
    offset: int = Query(0, ge=0),
    ordering: Ordering = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_chat_ownership(chat_id, current_user, db)
    
    query = db.query(UserState).filter(
        UserState.chat_id == chat_id,
        UserState.is_active == True
    )
    
    query = ordering.apply(query, UserState)
    
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return UserStatesList(
        items=[UserStateResponse.model_validate(s) for s in items],
        limit=limit,
        offset=offset,
        total=total
    )

@router.patch("/{state_id}", response_model=UserStateResponse)
def update_user_state(
    chat_id: UUID,
    state_id: UUID,
    state_data: UserStateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_chat_ownership(chat_id, current_user, db)
    
    user_state = db.query(UserState).filter(
        UserState.id == state_id,
        UserState.chat_id == chat_id,
        UserState.is_active == True
    ).first()
    if not user_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User state not found")
    
    try:
        if state_data.trusted is not None:
            user_state.trusted = state_data.trusted
        
        db.commit()
        db.refresh(user_state)
        
        logger.info(f"User state updated: {user_state.id}")
        return user_state
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user state"
        )

@router.post("/{state_id}/make-untrusted", response_model=UserStateResponse)
def make_untrusted(
    chat_id: UUID,
    state_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_chat_ownership(chat_id, current_user, db)
    
    user_state = db.query(UserState).filter(
        UserState.id == state_id,
        UserState.chat_id == chat_id,
        UserState.is_active == True
    ).first()
    if not user_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User state not found")
    
    try:
        user_state.trusted = False
        user_state.valid_messages = 0
        
        db.commit()
        db.refresh(user_state)
        
        logger.info(f"User state reset to untrusted: {user_state.id}")
        return user_state
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reset user state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user state"
        )
