from django.apps import AppConfig

class HostelmanagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.hostelmanagement"

    def ready(self):
        import apps.hostelmanagement.signals