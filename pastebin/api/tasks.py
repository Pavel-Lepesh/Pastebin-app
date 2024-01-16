from .celery import app
from .models import Note
from datetime import datetime
from django.core.cache import cache
from .s3_storage import s3_storage
import logging
import pytz


logging.basicConfig(level=logging.INFO)


@app.task
def auto_delete_when_expire():
    logging.info('Start checking the expiration of notes...')
    notes = Note.objects.all()
    for note in notes:
        try:
            if note.expiration < datetime.now(pytz.timezone('Europe/Minsk')):
                if cache.get(note.hash_link):
                    cache.delete(note.hash_link)
                s3_storage.delete_object(str(note.key_for_s3))
                note.delete()
                logging.info(f'"{note}" expired at {note.expiration}. Note deleted.')
        except Exception as error:
            logging.error(f'Note: {note}, error: {error}')
    logging.info('Checking completed.')
    return True
