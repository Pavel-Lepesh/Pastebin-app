import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastebin.settings')

app = Celery('api', broker_connection_retry=False,
             broker_connection_retry_on_startup=True)
app.conf.broker_url = 'redis://localhost:6379/1'
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.beat_schedule = {
    'generate_hash': {
        'task': 'api.tasks.auto_delete_when_expire',
        'schedule': crontab(),
    },
}
