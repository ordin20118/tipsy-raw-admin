from django.apps import AppConfig
from core.settings import SCHEDULER_DEFAULT
import os

class RawDataManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'raw_data_manager'

    def ready(self):
        if not os.environ.get('APP'):
            os.environ['APP'] = 'True'
            if SCHEDULER_DEFAULT:
                from . import scheduler            
                scheduler.start()