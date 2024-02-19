from .celery import app
from .models import Note
from datetime import datetime
from django.core.cache import cache
from .s3_storage import s3_storage
import logging
import pytz


logger = logging.getLogger(__name__)


@app.task
def auto_delete_when_expire():
    logger.info('Start checking the expiration of notes...')
    notes = Note.objects.all()
    for note in notes:
        if not note.expiration:
            continue

        try:
            if note.expiration < datetime.now(pytz.timezone('Europe/Minsk')):
                if cache.has_key(note.hash_link):
                    cache.delete(note.hash_link)
                s3_storage.delete_object(str(note.key_for_s3))
                note.delete()
                logger.info(f'"{note}" expired at {note.expiration}. Note deleted.')
        except Exception as error:
            logger.error(f'Note: {note}, error: {error}')
    logger.info('Checking completed.')
    return True
