from django.apps import AppConfig

class StoreConfig(AppConfig):
    # This ensures models use BigAutoField by default
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'