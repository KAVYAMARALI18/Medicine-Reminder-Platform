from django.apps import AppConfig
import os
import sys

class RemindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reminders'

    def ready(self):
        if 'runserver' not in sys.argv:
            return

        # The autoreloader starts the app twice; run the scheduler only in the serving process.
        if os.environ.get('RUN_MAIN') != 'true' and '--noreload' not in sys.argv:
            return

        from . import scheduler
        scheduler.start_scheduler()
