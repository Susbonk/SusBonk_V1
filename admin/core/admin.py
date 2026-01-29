from django.contrib import admin

from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "telegram_user_id",
        "discord_user_id",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("username", "email")
    list_filter = ("is_active",)


@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "platform_chat_id",
        "user",
        "title",
        "is_active",
        "enable_ai_check",
        "processed_messages",
        "spam_detected",
    )
    search_fields = ("title", "platform_chat_id")
    list_filter = ("type", "is_active", "enable_ai_check")


@admin.register(models.Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(models.CustomPrompt)
class CustomPromptAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("user",)


@admin.register(models.UserState)
class UserStateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat",
        "external_user_id",
        "trusted",
        "joined_at",
        "valid_messages",
    )
    list_filter = ("trusted", "chat")
    search_fields = ("external_user_id",)


@admin.register(models.ChatPrompt)
class ChatPromptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat",
        "prompt",
        "is_active",
        "priority",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "chat")


@admin.register(models.ChatCustomPrompt)
class ChatCustomPromptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat",
        "custom_prompt",
        "is_active",
        "priority",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "chat")


@admin.register(models.RuntimeStatistics)
class RuntimeStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "messages_checked",
        "ai_requests_made",
        "messages_deleted",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "name",
        "messages_checked",
        "ai_requests_made",
        "messages_deleted",
        "created_at",
        "updated_at",
    )

    search_fields = ("name",)
