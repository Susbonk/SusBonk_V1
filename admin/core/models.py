from django.db import models
from .models_base import BaseModel


class User(BaseModel):
    username = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    telegram_user_id = models.BigIntegerField(unique=True, null=True, blank=True)
    discord_user_id = models.BigIntegerField(unique=True, null=True, blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username or f"User {self.id}"


class Chat(BaseModel):
    CHAT_TYPES = [
        ('telegram', 'Telegram'),
        ('discord', 'Discord'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    type = models.CharField(max_length=16, choices=CHAT_TYPES)
    platform_chat_id = models.BigIntegerField(db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    chat_link = models.CharField(max_length=512, null=True, blank=True)
    
    enable_ai_check = models.BooleanField(default=False)
    enable_ai_moderation = models.BooleanField(default=True)
    
    clean_up_mentions = models.BooleanField(default=False)
    clean_up_emojis = models.BooleanField(default=False)
    clean_up_links = models.BooleanField(default=False)
    allowed_mentions = models.JSONField(null=True, blank=True)
    allowed_link_domains = models.JSONField(null=True, blank=True)
    
    processed_messages = models.IntegerField(default=0)
    spam_detected = models.IntegerField(default=0)
    messages_deleted = models.IntegerField(default=0)

    class Meta:
        db_table = 'chats'
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'platform_chat_id'],
                name='uk_chats_type_platform_chat_id'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_chats_user_active'),
            models.Index(fields=['type', 'platform_chat_id'], name='idx_chats_type_platform'),
        ]

    def __str__(self):
        return self.title or f"Chat {self.platform_chat_id}"


class Prompt(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    prompt_text = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'prompts'

    def __str__(self):
        return self.name or f"Prompt {self.id}"


class CustomPrompt(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_prompts')
    name = models.CharField(max_length=100, null=True, blank=True)
    prompt_text = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'custom_prompts'

    def __str__(self):
        return self.name or f"CustomPrompt {self.id}"


class UserState(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='user_states')
    external_user_id = models.BigIntegerField(db_index=True)
    trusted = models.BooleanField(default=False, db_index=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    valid_messages = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_states'
        indexes = [
            models.Index(fields=['chat', 'external_user_id'], name='idx_user_states_chat_extuser'),
            models.Index(fields=['external_user_id', 'trusted'], name='idx_user_states_extuser_trusted'),
        ]

    def __str__(self):
        return f"UserState {self.external_user_id} in {self.chat}"


class ChatPrompt(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_prompts')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='chat_prompts')
    priority = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'chat_prompts'
        constraints = [
            models.UniqueConstraint(
                fields=['chat', 'prompt'],
                name='uk_chat_prompts_chat_id_prompt_id'
            )
        ]

    def __str__(self):
        return f"{self.chat} - {self.prompt}"


class ChatCustomPrompt(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_custom_prompts')
    custom_prompt = models.ForeignKey(CustomPrompt, on_delete=models.CASCADE, related_name='chat_custom_prompts')
    priority = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'chat_custom_prompts'
        constraints = [
            models.UniqueConstraint(
                fields=['chat', 'custom_prompt'],
                name='uk_chat_custom_prompts_chat_id_custom_prompt_id'
            )
        ]

    def __str__(self):
        return f"{self.chat} - {self.custom_prompt}"


class RuntimeStatistics(BaseModel):
    name = models.CharField(max_length=100, unique=True, default='default_stats')
    messages_checked = models.IntegerField(default=0)
    ai_requests_made = models.IntegerField(default=0)
    messages_deleted = models.IntegerField(default=0)
    chat_messages_deleted = models.IntegerField(default=0)

    class Meta:
        db_table = 'runtime_statistics'
        verbose_name_plural = 'Runtime Statistics'

    def __str__(self):
        return self.name
