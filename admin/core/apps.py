from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from .db_triggers import ensure_updated_at_triggers

        post_migrate.connect(ensure_updated_at_triggers, sender=self)
