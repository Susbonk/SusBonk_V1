from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from core.db_helper import db_helper
from core.security import get_current_user
from models import Prompt, CustomPrompt, User
from schemas.prompt import (
    PromptResponse, PromptList, CustomPromptResponse, CustomPromptList,
    CustomPromptCreate, CustomPromptUpdate
)

router = APIRouter(prefix="/prompts", tags=["prompts"])

@router.get("", response_model=PromptList)
async def get_prompts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get all system prompts (read-only)."""
    result = await db.execute(select(Prompt).filter(Prompt.is_active == True))
    prompts = result.scalars().all()
    return PromptList(prompts=prompts)

@router.get("/custom", response_model=CustomPromptList)
async def get_custom_prompts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get all custom prompts for the current user."""
    result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.user_id == current_user.id,
            CustomPrompt.is_active == True
        )
    )
    prompts = result.scalars().all()
    return CustomPromptList(prompts=prompts)

@router.get("/custom/{custom_prompt_id}", response_model=CustomPromptResponse)
async def get_custom_prompt(
    custom_prompt_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Get a specific custom prompt."""
    result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.id == custom_prompt_id,
            CustomPrompt.user_id == current_user.id,
            CustomPrompt.is_active == True
        )
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    return prompt

@router.post("/custom", response_model=CustomPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_prompt(
    prompt_data: CustomPromptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Create a new custom prompt."""
    try:
        prompt = CustomPrompt(
            user_id=current_user.id,
            name=prompt_data.title,
            prompt_text=prompt_data.text,
            is_active=prompt_data.is_active
        )
        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        return prompt
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create custom prompt"
        )

@router.patch("/custom/{custom_prompt_id}", response_model=CustomPromptResponse)
async def update_custom_prompt(
    custom_prompt_id: UUID,
    prompt_update: CustomPromptUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Update a custom prompt."""
    result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.id == custom_prompt_id,
            CustomPrompt.user_id == current_user.id,
            CustomPrompt.is_active == True
        )
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    try:
        update_data = prompt_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "title":
                setattr(prompt, "name", value)
            elif field == "text":
                setattr(prompt, "prompt_text", value)
            else:
                setattr(prompt, field, value)
        
        await db.commit()
        await db.refresh(prompt)
        return prompt
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update custom prompt"
        )

@router.delete("/custom/{custom_prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_prompt(
    custom_prompt_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """Delete (soft-delete) a custom prompt."""
    result = await db.execute(
        select(CustomPrompt).filter(
            CustomPrompt.id == custom_prompt_id,
            CustomPrompt.user_id == current_user.id,
            CustomPrompt.is_active == True
        )
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom prompt not found")
    
    try:
        prompt.is_active = False
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete custom prompt"
        )
