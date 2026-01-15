from django.contrib import admin
from .models import User, Chat, Prompt, CustomPrompt, UserState, ChatPrompt, ChatCustomPrompt, RuntimeStatistics


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'telegram_user_id', 'discord_user_id', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'telegram_user_id', 'discord_user_id')
    list_filter = ('is_active', 'created_at')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'platform_chat_id', 'user', 'enable_ai_check', 'processed_messages', 'spam_detected', 'is_active')
    search_fields = ('title', 'platform_chat_id', 'user__username')
    list_filter = ('type', 'enable_ai_check', 'is_active', 'created_at')


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name', 'prompt_text')
    list_filter = ('is_active', 'created_at')


@admin.register(CustomPrompt)
class CustomPromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'created_at')
    search_fields = ('name', 'prompt_text', 'user__username')
    list_filter = ('is_active', 'created_at')


@admin.register(UserState)
class UserStateAdmin(admin.ModelAdmin):
    list_display = ('external_user_id', 'chat', 'trusted', 'valid_messages', 'joined_at', 'is_active')
    search_fields = ('external_user_id', 'chat__title')
    list_filter = ('trusted', 'is_active', 'joined_at')


@admin.register(ChatPrompt)
class ChatPromptAdmin(admin.ModelAdmin):
    list_display = ('chat', 'prompt', 'priority', 'is_active')
    search_fields = ('chat__title', 'prompt__name')
    list_filter = ('is_active', 'created_at')


@admin.register(ChatCustomPrompt)
class ChatCustomPromptAdmin(admin.ModelAdmin):
    list_display = ('chat', 'custom_prompt', 'priority', 'is_active')
    search_fields = ('chat__title', 'custom_prompt__name')
    list_filter = ('is_active', 'created_at')


@admin.register(RuntimeStatistics)
class RuntimeStatisticsAdmin(admin.ModelAdmin):
    list_display = ('name', 'messages_checked', 'ai_requests_made', 'messages_deleted', 'updated_at')
    search_fields = ('name',)
