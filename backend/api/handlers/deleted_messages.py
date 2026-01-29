import json
from uuid import UUID

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Query, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from api.deps.auth import get_current_user
from database import db_helper
from database.models import Chats, Users
from database.schemas.deleted_messages import (
    DeletedMessagesList,
    DeletedMessageResponse,
)
from logger import get_logger

log = get_logger(__name__)
get_session = db_helper.session_getter


def get_redis():
    # TODO: Move URL to env
    return redis.from_url("redis://redis:6379", decode_responses=True)


router = APIRouter(prefix="/deleted-messages", tags=["deleted_messages"])


@router.get("/{chat_id}", response_model=DeletedMessagesList)
async def get_deleted_messages(
    chat_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(get_current_user),
    r=Depends(get_redis),
    limit: int = Query(50, ge=1, le=200),
) -> DeletedMessagesList:
    stmt = select(Chats).where(
        Chats.id == chat_id, Chats.user_id == current_user.id
    )
    res = await session.execute(stmt)
    chat = res.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    stream_key = f"deleted_messages:{chat_id}"

    try:
        rows = await r.xrevrange(stream_key, max="+", min="-", count=limit)
    except Exception:
        log.exception("Redis read failed")
        raise HTTPException(status_code=502, detail="Redis error")

    items: list[DeletedMessageResponse] = []
    for _entry_id, fields in rows:
        payload = fields.get("payload")
        if not payload:
            continue

        try:
            obj = json.loads(payload)

            # TODO: Add Discord support
            if "platform_user_id" not in obj and "telegram_user_id" in obj:
                obj["platform_user_id"] = obj.pop("telegram_user_id")

            if "user_state_id" not in obj and "user_state_uuid" in obj:
                obj["user_state_id"] = obj.pop("user_state_uuid")

            items.append(DeletedMessageResponse(**obj))

        except (json.JSONDecodeError, ValidationError) as e:
            log.warning(
                f"Failed to parse deleted message payload entry={_entry_id}: {e}"  # noqa: E501
            )

    return DeletedMessagesList(items=items)
