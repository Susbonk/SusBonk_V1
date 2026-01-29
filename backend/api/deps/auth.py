from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.security import decode_token
from database import db_helper
from database.models import Users
from logger import get_logger


log = get_logger(__name__)

bearer = HTTPBearer(auto_error=False)
get_session = db_helper.session_getter


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> Users:
    log.debug("Processing authentication request")
    if creds is None or creds.scheme.lower() != "bearer":
        log.warning("Authentication failed: No bearer token provided")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(creds.credentials)
        user_id = UUID(payload["sub"])
        log.debug(f"Decoded token for user ID: {user_id}")
    except Exception as e:
        log.error(f"Authentication failed: Invalid token - {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

    stmt = select(Users).where(
        Users.id == user_id,
        Users.is_active == True,  # noqa: E712
    )
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if user is None:
        log.warning(f"Authentication failed: User not found or inactive - {user_id}")
        raise HTTPException(status_code=401, detail="User not found")

    log.info(f"Successfully authenticated user: {user.id}")
    return user
