from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.auth import get_current_user
from database import db_helper
from database.models import (
    Chats,
    Users,
    Prompts,
    CustomPrompts,
    ChatPrompts,
    ChatCustomPrompts,
)
from database.schemas.chat import (
    ChatSettingsResponse,
    ChatSettingsUpdate,
    ChatsList,
)
from database.schemas import (
    ChatPromptLinkCreate,
    ChatCustomPromptLinkCreate,
    ChatPromptLinkResponse,
    ChatCustomPromptLinkResponse,
    ChatLinksResponse,
)
from logger import get_logger


log = get_logger(__name__)

get_session = db_helper.session_getter

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=ChatsList)
async def list_my_chats(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),
    chat_type: Optional[str] = Query(None),
) -> ChatsList:
    log.debug(
        f"Listing chats for user: {current_user.id}, limit: {limit}, offset: {offset}"  # noqa: E501
    )  # noqa: E501
    stmt = (
        select(Chats)
        .where(Chats.user_id == current_user.id)
        .offset(offset)
        .limit(limit)
    )

    if is_active is not None:
        stmt = stmt.where(Chats.is_active == is_active)
        log.debug(f"Filtering by is_active: {is_active}")

    if chat_type is not None:
        stmt = stmt.where(Chats.type == chat_type)
        log.debug(f"Filtering by chat_type: {chat_type}")

    res = await session.execute(stmt)
    items = res.scalars().all()

    log.info(f"Found {len(items)} chats for user: {current_user.id}")
    parsed = [ChatSettingsResponse.model_validate(x) for x in items]
    return ChatsList(chats=parsed)


@router.get("/{chat_id}", response_model=ChatSettingsResponse)
async def get_my_chat(
    chat_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ChatSettingsResponse:
    log.debug(f"Retrieving chat {chat_id} for user: {current_user.id}")
    stmt = select(Chats).where(
        Chats.id == chat_id,
        Chats.user_id == current_user.id,
    )
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        log.warning(f"Chat {chat_id} not found for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Chat not found")

    log.info(f"Successfully retrieved chat {chat_id} for user: {current_user.id}")  # noqa: E501
    return ChatSettingsResponse.model_validate(obj)


@router.patch("/{chat_id}", response_model=ChatSettingsResponse)
async def update_my_chat_settings(
    chat_id: UUID,
    payload: ChatSettingsUpdate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ChatSettingsResponse:
    log.info(f"Updating chat settings for chat {chat_id} by user: {current_user.id}")  # noqa: E501
    stmt = select(Chats).where(
        Chats.id == chat_id,
        Chats.user_id == current_user.id,
    )
    res = await session.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj is None:
        log.warning(f"Chat {chat_id} not found for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Chat not found")

    data = payload.model_dump(exclude_unset=True)
    log.debug(f"Updating chat {chat_id} with data: {data}")
    for k, v in data.items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)

    log.info(f"Successfully updated chat settings for chat {chat_id}")
    return ChatSettingsResponse.model_validate(obj)


async def _get_my_chat_or_404(
    session: AsyncSession,
    current_user: Users,
    chat_id: UUID,
) -> Chats:
    stmt = select(Chats).where(
        Chats.id == chat_id, Chats.user_id == current_user.id
    )
    res = await session.execute(stmt)
    chat = res.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.get("/{chat_id}/linked_prompts", response_model=ChatLinksResponse)
async def list_chat_links(
    chat_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> ChatLinksResponse:
    await _get_my_chat_or_404(session, current_user, chat_id)

    stmt_p = select(ChatPrompts).where(ChatPrompts.chat_id == chat_id)
    stmt_cp = select(ChatCustomPrompts).where(
        ChatCustomPrompts.chat_id == chat_id
    )

    res_p = await session.execute(stmt_p)
    res_cp = await session.execute(stmt_cp)

    links_p = res_p.scalars().all()
    links_cp = res_cp.scalars().all()

    return ChatLinksResponse(
        prompts=[ChatPromptLinkResponse.model_validate(x) for x in links_p],
        custom_prompts=[
            ChatCustomPromptLinkResponse.model_validate(x) for x in links_cp
        ],
    )


@router.post(
    "/{chat_id}/prompts",
    response_model=ChatPromptLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_prompt_link(
    chat_id: UUID,
    payload: ChatPromptLinkCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> ChatPromptLinkResponse:
    await _get_my_chat_or_404(session, current_user, chat_id)

    # optional: validate prompt exists (read-only global list)
    res = await session.execute(
        select(Prompts).where(
            Prompts.id == payload.prompt_id
        )
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # prevent duplicates
    stmt_exists = select(ChatPrompts).where(
        ChatPrompts.chat_id == chat_id,
        ChatPrompts.prompt_id == payload.prompt_id,
    )
    res_exists = await session.execute(stmt_exists)
    if res_exists.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Link already exists")

    obj = ChatPrompts(
        chat_id=chat_id,
        prompt_id=payload.prompt_id,
        is_active=payload.is_active,
        priority=payload.priority,
        threshold=payload.threshold,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    return ChatPromptLinkResponse.model_validate(obj)


@router.delete(
    "/{chat_id}/prompts/{prompt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat_prompt_link(
    chat_id: UUID,
    prompt_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> None:
    await _get_my_chat_or_404(session, current_user, chat_id)

    stmt_find = select(ChatPrompts).where(
        ChatPrompts.chat_id == chat_id,
        ChatPrompts.prompt_id == prompt_id,
    )
    res = await session.execute(stmt_find)
    obj = res.scalar_one_or_none()

    if obj is None:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(obj)
    await session.commit()
    return None


@router.post(
    "/{chat_id}/custom-prompts",
    response_model=ChatCustomPromptLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_custom_prompt_link(
    chat_id: UUID,
    payload: ChatCustomPromptLinkCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> ChatCustomPromptLinkResponse:
    await _get_my_chat_or_404(session, current_user, chat_id)

    # validate custom prompt belongs to user
    res = await session.execute(
        select(CustomPrompts).where(
            CustomPrompts.id == payload.custom_prompt_id,
            CustomPrompts.user_id == current_user.id,
        )
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Custom prompt not found")

    # prevent duplicates
    stmt_exists = select(ChatCustomPrompts).where(
        ChatCustomPrompts.chat_id == chat_id,
        ChatCustomPrompts.custom_prompt_id == payload.custom_prompt_id,
    )
    res_exists = await session.execute(stmt_exists)
    if res_exists.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Link already exists")

    obj = ChatCustomPrompts(
        chat_id=chat_id,
        custom_prompt_id=payload.custom_prompt_id,
        is_active=payload.is_active,
        priority=payload.priority,
        threshold=payload.threshold,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    return ChatCustomPromptLinkResponse.model_validate(obj)


@router.delete(
    "/{chat_id}/custom-prompts/{custom_prompt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat_custom_prompt_link(
    chat_id: UUID,
    custom_prompt_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> None:
    await _get_my_chat_or_404(session, current_user, chat_id)

    stmt_find = select(ChatCustomPrompts).where(
        ChatCustomPrompts.chat_id == chat_id,
        ChatCustomPrompts.custom_prompt_id == custom_prompt_id,
    )
    res = await session.execute(stmt_find)
    obj = res.scalar_one_or_none()

    if obj is None:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(obj)
    await session.commit()
    return None
