from django.apps import AppConfig


class FeemanagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.feemanagement'

    def ready(self):
        import apps.feemanagement.signals
