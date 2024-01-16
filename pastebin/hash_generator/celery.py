import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastebin.settings')

app = Celery('hash_generator', broker_connection_retry=False,
             broker_connection_retry_on_startup=True)
app.conf.broker_url = f'redis://{os.getenv("CELERY_HOST_REDIS")}:6379/1'  # для локальных тестов localhost
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.beat_schedule = {
    'generate_hash': {
        'task': 'hash_generator.tasks.start_generator',
        'schedule': crontab(),
    },
}
