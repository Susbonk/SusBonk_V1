from fastapi import APIRouter

from .auth import router as auth_router
from .prompt import router as prompts_router
from .chat import router as chat_router
from .user_state import router as user_state_router
from .deleted_messages import router as deleted_messages_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(prompts_router)
router.include_router(chat_router)
router.include_router(user_state_router)
router.include_router(deleted_messages_router)
