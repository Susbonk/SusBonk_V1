from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import Ordering
from api.deps.auth import get_current_user
from database import db_helper
from database.models import CustomPrompts, Prompts, Users
from database.schemas import (
    CustomPromptCreate,
    CustomPromptResponse,
    CustomPromptUpdate,
    CustomPromptsList,
    PromptResponse,
    PromptsList,
)
from logger import get_logger

log = get_logger(__name__)

get_session = db_helper.session_getter
router = APIRouter(prefix="/prompts", tags=["prompts"])

prompts_ordering = Ordering(
    model=Prompts,
    allowed_fields=["id", "name", "created_at", "updated_at", "is_active"],
    default_field="id",
)

custom_prompts_ordering = Ordering(
    model=CustomPrompts,
    allowed_fields=[
        "id",
        "name",
        "created_at",
        "updated_at",
        "is_active",
        "user_id",
    ],
    default_field="id",
)

# -------------------- Prompts (read-only list) --------------------


@router.get("", response_model=PromptsList)
async def list_prompts(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),
    order: Optional[str] = Query(None),
    order_desc: bool = Query(False),
) -> PromptsList:
    log.debug(
        f"Listing prompts, limit: {limit}, offset: {offset}, is_active: {is_active}, order: {order}, order_desc: {order_desc}"  # noqa: E501
    )
    stmt = select(Prompts)

    if is_active is not None:
        stmt = stmt.where(Prompts.is_active == is_active)
        log.debug(f"Filtering by is_active: {is_active}")

    stmt = (
        stmt.order_by(
            prompts_ordering.order_by(
                order=order,
                order_desc=order_desc,
            )
        )
        .offset(offset)
        .limit(limit)
    )

    res = await session.execute(stmt)
    items = res.scalars().all()

    log.info(f"Found {len(items)} prompts")
    return PromptsList(
        prompts=[PromptResponse.model_validate(x) for x in items]
    )


# -------------------- CustomPrompts (CRUD) --------------------
# IMPORTANT: keep these BEFORE "/{prompt_id}" route


@router.get("/custom", response_model=CustomPromptsList)
async def list_custom_prompts(
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),
    order: Optional[str] = Query(None),
    order_desc: bool = Query(False),
) -> CustomPromptsList:
    log.debug(
        f"Listing custom prompts for user: {current_user.id}, limit: {limit}, offset: {offset}, is_active: {is_active}, order: {order}, order_desc: {order_desc}"  # noqa: E501
    )
    stmt = select(CustomPrompts).where(CustomPrompts.user_id == current_user.id)  # noqa: E501

    if is_active is not None:
        stmt = stmt.where(CustomPrompts.is_active == is_active)
        log.debug(f"Filtering by is_active: {is_active}")

    stmt = (
        stmt.order_by(
            custom_prompts_ordering.order_by(
                order=order,
                order_desc=order_desc,
            )
        )
        .offset(offset)
        .limit(limit)
    )

    res = await session.execute(stmt)
    items = res.scalars().all()

    log.info(f"Found {len(items)} custom prompts for user: {current_user.id}")
    return CustomPromptsList(
        prompts=[CustomPromptResponse.model_validate(x) for x in items]
    )


@router.get("/custom/{custom_prompt_id}", response_model=CustomPromptResponse)
async def get_custom_prompt(
    custom_prompt_id: UUID,
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CustomPromptResponse:
    log.debug(
        f"Retrieving custom prompt {custom_prompt_id} for user: {current_user.id}"  # noqa: E501
    )
    stmt = select(CustomPrompts).where(
        CustomPrompts.id == custom_prompt_id,
        CustomPrompts.user_id == current_user.id,
    )
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        log.warning(
            f"Custom prompt {custom_prompt_id} not found for user: {current_user.id}"  # noqa: E501
        )
        raise HTTPException(status_code=404, detail="Custom prompt not found")

    log.info(
        f"Successfully retrieved custom prompt {custom_prompt_id} for user: {current_user.id}"  # noqa: E501
    )
    return CustomPromptResponse.model_validate(obj)


@router.post(
    "/custom",
    response_model=CustomPromptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_custom_prompt(
    payload: CustomPromptCreate,
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CustomPromptResponse:
    log.info(f"Creating custom prompt for user: {current_user.id}")
    obj = CustomPrompts(
        user_id=current_user.id,
        is_active=payload.is_active,
        name=payload.title,
        prompt_text=payload.text,
    )

    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    log.info(
        f"Successfully created custom prompt {obj.id} for user: {current_user.id}"  # noqa: E501
    )
    return CustomPromptResponse.model_validate(obj)


@router.patch(
    "/custom/{custom_prompt_id}",
    response_model=CustomPromptResponse,
)
async def update_custom_prompt(
    custom_prompt_id: UUID,
    payload: CustomPromptUpdate,
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CustomPromptResponse:
    log.info(
        f"Updating custom prompt {custom_prompt_id} for user: {current_user.id}"  # noqa: E501
    )
    stmt = select(CustomPrompts).where(
        CustomPrompts.id == custom_prompt_id,
        CustomPrompts.user_id == current_user.id,
    )
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        log.warning(
            f"Custom prompt {custom_prompt_id} not found for user: {current_user.id}"  # noqa: E501
        )
        raise HTTPException(status_code=404, detail="Custom prompt not found")

    data = payload.model_dump(exclude_unset=True)
    log.debug(f"Updating custom prompt {custom_prompt_id} with data: {data}")

    if "title" in data:
        obj.name = data.pop("title")

    if "text" in data:
        obj.prompt_text = data.pop("text")

    for k, v in data.items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)

    log.info(f"Successfully updated custom prompt {custom_prompt_id}")
    return CustomPromptResponse.model_validate(obj)


@router.delete(
    "/custom/{custom_prompt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_custom_prompt(
    custom_prompt_id: UUID,
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    log.info(
        f"Deleting custom prompt {custom_prompt_id} for user: {current_user.id}"  # noqa: E501
    )
    stmt = select(CustomPrompts).where(
        CustomPrompts.id == custom_prompt_id,
        CustomPrompts.user_id == current_user.id,
    )
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        log.warning(
            f"Custom prompt {custom_prompt_id} not found for user: {current_user.id}"  # noqa: E501
        )
        raise HTTPException(status_code=404, detail="Custom prompt not found")

    await session.delete(obj)
    await session.commit()

    log.info(f"Successfully deleted custom prompt {custom_prompt_id}")
    return None


# -------------------- Prompts (read-only by id) --------------------
# MUST be after "/custom" routes


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> PromptResponse:
    log.debug(f"Retrieving prompt {prompt_id}")
    stmt = select(Prompts).where(Prompts.id == prompt_id)
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        log.warning(f"Prompt {prompt_id} not found")
        raise HTTPException(status_code=404, detail="Prompt not found")

    log.info(f"Successfully retrieved prompt {prompt_id}")
    return PromptResponse.model_validate(obj)
