import threading
import os
from django.apps import AppConfig

class ModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'models'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .bot_setup import start_bot
            threading.Thread(target=start_bot, daemon=True).start()