# hook signals into the app

from django.apps import AppConfig

class BagConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bag'

    def ready(self):
        import bag.signals
