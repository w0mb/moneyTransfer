from django.apps import AppConfig


class MainConfig(AppConfig):
    verbose_name = "Движение денежных средств"
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'