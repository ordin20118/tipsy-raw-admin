from django.apps import AppConfig
from core.settings import SCHEDULER_DEFAULT
from core.openai_settings import OPENAI_SECRET_KEY, OPENAI_URL_PROMPT
import os
import openai
class RawDataManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'raw_data_manager'

    openai.api_key = OPENAI_SECRET_KEY

    def ready(self):
        if not os.environ.get('APP'):
            os.environ['APP'] = 'True'
            if SCHEDULER_DEFAULT:
                from . import scheduler            
                scheduler.start()