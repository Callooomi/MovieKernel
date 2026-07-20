from django.apps import AppConfig


class TenableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenable'

    def ready(self):
        from . import signals  # noqa: F401  (registers the post_save handler)
