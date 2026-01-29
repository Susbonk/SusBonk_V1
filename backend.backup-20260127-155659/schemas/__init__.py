# Pydantic schemas
from .auth import *
from .chat import *
from .prompt import *
from .user_state import *
from .deleted_messages import *
from .chat_prompt_links import *

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin", 
    "Token",
    "UserResponse",
    "TelegramConnectResponse",
    # Chat schemas
    "ChatResponse",
    "ChatUpdate",
    "ChatList",
    # Prompt schemas
    "PromptResponse",
    "PromptList",
    "CustomPromptResponse",
    "CustomPromptCreate",
    "CustomPromptUpdate",
    "CustomPromptList",
    # User state schemas
    "UserStateResponse",
    "UserStateUpdate",
    "UserStatesList",
    # Deleted messages schemas
    "DeletedMessageResponse",
    "DeletedMessagesList",
    # Chat-prompt link schemas
    "ChatPromptLinkResponse",
    "ChatPromptLinkCreate",
    "ChatPromptLinksList",
    "ChatCustomPromptLinkResponse",
    "ChatCustomPromptLinkCreate",
    "ChatCustomPromptLinksList",
]
