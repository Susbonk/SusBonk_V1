from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from database.helper import get_db
from database.models import User, Prompt, CustomPrompt
from database.schemas.prompt import (
    PromptResponse, PromptList,
    CustomPromptCreate, CustomPromptUpdate, CustomPromptResponse, CustomPromptList
)
from api.deps.auth import get_current_user
from logger import logger

router = APIRouter(prefix="/prompts", tags=["prompts"])

# -------------------- System Prompts (read-only list) --------------------

@router.get("", response_model=PromptList)
async def list_prompts(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),
    order: Optional[str] = Query(None),
    order_desc: bool = Query(False),
):
    """List all system prompts (read-only)."""
    query = select(Prompt)
    
    # Apply is_active filter
    if is_active is not None:
        query = query.filter(Prompt.is_active == is_active)
    else:
        query = query.filter(Prompt.is_active == True)
    
    # Apply ordering
    if order:
        order_column = getattr(Prompt, order, None)
        if order_column is not None:
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return PromptList(prompts=[PromptResponse.model_validate(p) for p in items])


# -------------------- Custom Prompts (CRUD) --------------------
# IMPORTANT: keep these BEFORE "/{prompt_id}" route

@router.get("/custom", response_model=CustomPromptList)
async def list_custom_prompts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),
    order: Optional[str] = Query(None),
    order_desc: bool = Query(False),
):
    """List custom prompts for the current user."""
    query = select(CustomPrompt).filter(CustomPrompt.user_id == current_user.id)
    
    # Apply is_active filter
    if is_active is not None:
        query = query.filter(CustomPrompt.is_active == is_active)
    else:
        query = query.filter(CustomPrompt.is_active == True)
    
    # Apply ordering
    if order:
        order_column = getattr(CustomPrompt, order, None)
        if order_column is not None:
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return CustomPromptList(prompts=[CustomPromptResponse.model_validate(p) for p in items])


@router.get("/custom/{custom_prompt_id}", response_model=CustomPromptResponse)
async def get_custom_prompt(
    custom_prompt_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific custom prompt by ID."""
    result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.id == custom_prompt_id,
            CustomPrompt.user_id == current_user.id,
        )
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    return CustomPromptResponse.model_validate(prompt)


@router.post("/custom", response_model=CustomPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_prompt(
    payload: CustomPromptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom prompt."""
    try:
        prompt = CustomPrompt(
            user_id=current_user.id,
            name=payload.title,
            prompt_text=payload.text,
            is_active=payload.is_active
        )
        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        
        logger.info(f"Custom prompt created: {prompt.id} by user {current_user.id}")
        return CustomPromptResponse.model_validate(prompt)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create custom prompt"
        )


@router.patch("/custom/{custom_prompt_id}", response_model=CustomPromptResponse)
async def update_custom_prompt(
    custom_prompt_id: UUID,
    payload: CustomPromptUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a custom prompt."""
    result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.id == custom_prompt_id,
            CustomPrompt.user_id == current_user.id,
        )
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    try:
        data = payload.model_dump(exclude_unset=True)
        # Map title -> name, text -> prompt_text
        if 'title' in data:
            prompt.name = data['title']
        if 'text' in data:
            prompt.prompt_text = data['text']
        if 'is_active' in data:
            prompt.is_active = data['is_active']
        
        await db.commit()
        await db.refresh(prompt)
        
        logger.info(f"Custom prompt updated: {prompt.id}")
        return CustomPromptResponse.model_validate(prompt)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update custom prompt"
        )


@router.delete("/custom/{custom_prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_prompt(
    custom_prompt_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete (soft-delete) a custom prompt."""
    result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.id == custom_prompt_id,
            CustomPrompt.user_id == current_user.id,
        )
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    try:
        prompt.is_active = False
        await db.commit()
        logger.info(f"Custom prompt deleted: {prompt.id}")
        return None
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete custom prompt"
        )


# -------------------- System Prompts (read-only by id) --------------------
# MUST be after "/custom" routes

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific system prompt by ID."""
    result = await db.execute(select(Prompt).filter(Prompt.id == prompt_id))
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return PromptResponse.model_validate(prompt)
