from .generator import generator
from .celery import app


@app.task
def start_generator():
    generator.start_generate()
    return True
