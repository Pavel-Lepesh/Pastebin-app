from .celery import app
from .models import Note
from datetime import datetime
import logging
import pytz


logging.basicConfig(level=logging.INFO)


@app.task
def auto_delete_when_expire():
    logging.info('Start checking the expiration of notes...')
    notes = Note.objects.all()
    for note in notes:
        if note.expiration < datetime.now(pytz.timezone('Europe/Minsk')):
            note.delete()
            logging.info(f'"{note}" expired at {note.expiration}. Note deleted.')
    logging.info('Checking completed.')
    return True
