from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.auth import get_current_user
from database import db_helper
from database.models import Chats, UserStates
from database.schemas.user_state import (
    UserStateResponse,
    UserStatesList,
    UserStateUpdate,
)
from logger import get_logger

log = get_logger(__name__)
get_session = db_helper.session_getter

router = APIRouter(prefix="/chats", tags=["user_states"])


async def _ensure_chat_owned(
    session: AsyncSession,
    chat_id: UUID,
    current_user,
) -> None:
    stmt = select(Chats.id).where(
        Chats.id == chat_id,
        Chats.user_id == current_user.id,
    )
    res = await session.execute(stmt)
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Chat not found")


@router.get("/{chat_id}/user-states", response_model=UserStatesList)
async def list_chat_user_states(
    chat_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    trusted: Optional[bool] = Query(None),
    external_user_id: Optional[int] = Query(None),
) -> UserStatesList:
    await _ensure_chat_owned(session, chat_id, current_user)

    stmt = select(UserStates).where(UserStates.chat_id == chat_id)
    count_stmt = select(func.count()).select_from(UserStates).where(UserStates.chat_id == chat_id)

    if trusted is not None:
        stmt = stmt.where(UserStates.trusted == trusted)
        count_stmt = count_stmt.where(UserStates.trusted == trusted)

    if external_user_id is not None:
        stmt = stmt.where(UserStates.external_user_id == external_user_id)
        count_stmt = count_stmt.where(UserStates.external_user_id == external_user_id)

    stmt = stmt.order_by(UserStates.updated_at.desc()).offset(offset).limit(limit)

    total = (await session.execute(count_stmt)).scalar_one()
    res = await session.execute(stmt)
    items = res.scalars().all()

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
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
) -> UserStateResponse:
    await _ensure_chat_owned(session, chat_id, current_user)

    stmt = select(UserStates).where(
        UserStates.id == state_id,
        UserStates.chat_id == chat_id,
    )
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        raise HTTPException(status_code=404, detail="User state not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)
    return UserStateResponse.model_validate(obj)


@router.post("/{chat_id}/user-states/{state_id}/make-untrusted", response_model=UserStateResponse)
async def make_untrusted(
    chat_id: UUID,
    state_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
) -> UserStateResponse:
    await _ensure_chat_owned(session, chat_id, current_user)

    stmt = select(UserStates).where(
        UserStates.id == state_id,
        UserStates.chat_id == chat_id,
    )
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        raise HTTPException(status_code=404, detail="User state not found")

    obj.trusted = False
    obj.joined_at = None
    obj.valid_messages = 0

    # Reset joined_at to current time
    obj.joined_at = (await session.execute(select(func.now()))).scalar_one()

    await session.commit()
    await session.refresh(obj)
    return UserStateResponse.model_validate(obj)
