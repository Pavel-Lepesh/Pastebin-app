from .generator import HashGenerator
from .celery import app


@app.task
def start_generator():
    HashGenerator().__init__()
    return True
