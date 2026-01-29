from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .models_base import BaseModel


class User(BaseModel):
    username = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    email = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    password_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    telegram_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
    )
    discord_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "users"


class Chat(BaseModel):
    class ChatType(models.TextChoices):
        TELEGRAM = "telegram", "telegram"
        DISCORD = "discord", "discord"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chats",
    )
    type = models.CharField(max_length=16, choices=ChatType.choices)
    platform_chat_id = models.BigIntegerField()

    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    chat_link = models.CharField(
        max_length=512,
        null=True,
        blank=True,
    )

    enable_ai_check = models.BooleanField(default=False)

    cleanup_mentions = models.BooleanField(default=False)
    allowed_mentions = models.JSONField(
        null=True,
        blank=True,
    )

    cleanup_emojis = models.BooleanField(default=False)
    max_emoji_count = models.IntegerField(default=5)

    cleanup_links = models.BooleanField(default=False)

    allowed_link_domains = models.JSONField(
        null=True,
        blank=True,
    )

    cleanup_emails = models.BooleanField(default=False)

    prompts = models.ManyToManyField(
        "Prompt",
        through="ChatPrompt",
        related_name="chats",
        blank=True,
    )
    custom_prompts = models.ManyToManyField(
        "CustomPrompt",
        through="ChatCustomPrompt",
        related_name="chats",
        blank=True,
    )

    processed_messages = models.IntegerField(default=0)
    spam_detected = models.IntegerField(default=0)
    messages_deleted = models.IntegerField(default=0)

    min_messages_required = models.IntegerField(default=20)
    min_observation_minutes = models.IntegerField(default=60)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "chats"
        constraints = [
            models.UniqueConstraint(
                fields=["type", "platform_chat_id"],
                name="uk_chats_type_platform_chat_id",
            )
        ]


class Prompt(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    prompt_text = models.TextField(null=True, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "prompts"


class CustomPrompt(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="custom_prompts"
    )

    name = models.CharField(max_length=100, null=True, blank=True)
    prompt_text = models.TextField(null=True, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "custom_prompts"


class UserState(BaseModel):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="user_states",
    )
    external_user_id = models.BigIntegerField()

    trusted = models.BooleanField(default=False)

    joined_at = models.DateTimeField(null=True, blank=True)
    valid_messages = models.IntegerField(default=0)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "user_states"
        indexes = [
            models.Index(
                fields=["chat", "external_user_id"],
                name="idx_user_states_chat_extuser",
            ),
        ]


class ChatPrompt(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)

    priority = models.IntegerField(null=True, blank=True)
    threshold = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "chat_prompts"
        constraints = [
            models.UniqueConstraint(
                fields=["chat", "prompt"],
                name="uk_chat_prompts_chat_id_prompt_id",
            ),
        ]


class ChatCustomPrompt(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    custom_prompt = models.ForeignKey(CustomPrompt, on_delete=models.CASCADE)

    priority = models.IntegerField(null=True, blank=True)
    threshold = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "chat_custom_prompts"
        constraints = [
            models.UniqueConstraint(
                fields=["chat", "custom_prompt"],
                name="uk_chat_custom_prompts_chat_id_custom_prompt_id",
            ),
        ]


class RuntimeStatistics(BaseModel):
    """
    Simple model for tracking runtime stats - messages checked,
    AI requests, messages deleted
    """

    messages_checked = models.IntegerField(default=0)
    ai_requests_made = models.IntegerField(default=0)
    messages_deleted = models.IntegerField(default=0)

    # e.g. Telegram | Discord or default
    name = models.CharField(
        max_length=100,
        default="default_stats",
        unique=True,
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        db_table = "runtime_statistics"
