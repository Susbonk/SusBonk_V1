from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(self.create_db_triggers, sender=self)

    def create_db_triggers(self, sender, **kwargs):
        from . import db_triggers
        db_triggers.install_triggers()
