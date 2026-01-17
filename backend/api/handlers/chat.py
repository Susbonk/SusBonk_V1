from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from database.helper import get_db
from database.models import User, Chat
from database.schemas.chat import ChatResponse, ChatUpdate, ChatList
from api.deps.auth import get_current_user
from api.deps.ordering import Ordering
from logger import logger

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("", response_model=ChatList)
def list_chats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ordering: Ordering = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Chat).filter(
        Chat.user_id == current_user.id,
        Chat.is_active == True
    )
    
    query = ordering.apply(query, Chat)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ChatList(items=items, total=total, page=page, page_size=page_size)

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
        Chat.is_active == True
    ).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat

@router.patch("/{chat_id}", response_model=ChatResponse)
def update_chat(
    chat_id: UUID,
    chat_data: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
        Chat.is_active == True
    ).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    try:
        update_data = chat_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chat, field, value)
        
        db.commit()
        db.refresh(chat)
        
        logger.info(f"Chat updated: {chat.id}")
        return chat
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat"
        )
