from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from database.helper import get_db
from database.models import User, Prompt, CustomPrompt
from database.schemas.prompt import (
    PromptResponse, PromptList,
    CustomPromptCreate, CustomPromptUpdate, CustomPromptResponse, CustomPromptList
)
from api.deps.auth import get_current_user
from api.deps.ordering import Ordering
from logger import logger

router = APIRouter(prefix="/prompts", tags=["prompts"])

# Custom Prompts (full CRUD) - Must come before /{prompt_id} to avoid route conflict
@router.get("/custom", response_model=CustomPromptList)
def list_custom_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ordering: Ordering = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(CustomPrompt).filter(
        CustomPrompt.user_id == current_user.id,
        CustomPrompt.is_active == True
    )
    
    query = ordering.apply(query, CustomPrompt)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return CustomPromptList(items=items, total=total, page=page, page_size=page_size)

@router.get("/custom/{prompt_id}", response_model=CustomPromptResponse)
def get_custom_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompt = db.query(CustomPrompt).filter(
        CustomPrompt.id == prompt_id,
        CustomPrompt.user_id == current_user.id,
        CustomPrompt.is_active == True
    ).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    return prompt

@router.post("/custom", response_model=CustomPromptResponse, status_code=status.HTTP_201_CREATED)
def create_custom_prompt(
    prompt_data: CustomPromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        prompt = CustomPrompt(
            user_id=current_user.id,
            name=prompt_data.name,
            prompt_text=prompt_data.prompt_text
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        logger.info(f"Custom prompt created: {prompt.id} by user {current_user.id}")
        return prompt
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create custom prompt"
        )

@router.patch("/custom/{prompt_id}", response_model=CustomPromptResponse)
def update_custom_prompt(
    prompt_id: UUID,
    prompt_data: CustomPromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompt = db.query(CustomPrompt).filter(
        CustomPrompt.id == prompt_id,
        CustomPrompt.user_id == current_user.id,
        CustomPrompt.is_active == True
    ).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    try:
        if prompt_data.name is not None:
            prompt.name = prompt_data.name
        if prompt_data.prompt_text is not None:
            prompt.prompt_text = prompt_data.prompt_text
        
        db.commit()
        db.refresh(prompt)
        
        logger.info(f"Custom prompt updated: {prompt.id}")
        return prompt
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update custom prompt"
        )

@router.delete("/custom/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_custom_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompt = db.query(CustomPrompt).filter(
        CustomPrompt.id == prompt_id,
        CustomPrompt.user_id == current_user.id,
        CustomPrompt.is_active == True
    ).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    try:
        prompt.is_active = False
        db.commit()
        logger.info(f"Custom prompt deleted: {prompt.id}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete custom prompt"
        )

# System Prompts (read-only) - After custom routes to avoid conflicts
@router.get("", response_model=PromptList)
def list_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    ordering: Ordering = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Prompt).filter(Prompt.is_active == True)
    
    if search:
        query = query.filter(Prompt.name.ilike(f"%{search}%"))
    
    query = ordering.apply(query, Prompt)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PromptList(items=items, total=total, page=page, page_size=page_size)

@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.is_active == True).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return prompt
