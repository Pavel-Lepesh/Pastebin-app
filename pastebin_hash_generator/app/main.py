from contextlib import asynccontextmanager
from fastapi import FastAPI, status
import asyncio
from redis import asyncio as aioredis
import pika

from app.producer import producer_func
from app.generator import generator_func
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True,
        )
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(settings.RABBITMQ_HOST, settings.RABBITMQ_PORT, settings.RABBITMQ_VIRTUAL_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    task_generator = asyncio.create_task(generator_func(redis=redis), name='hash_generator')
    task_producer = asyncio.create_task(producer_func(redis=redis, connection=connection), name='producer')
    yield
    await redis.close()
    connection.close()


app = FastAPI(lifespan=lifespan)


@app.get("/cancel-generate", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_generate():
    for task in asyncio.all_tasks():
        if task.get_name() == 'hash_generator':
            task.cancel()


@app.get("/cancel-produce", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_produce():
    for task in asyncio.all_tasks():
        if task.get_name() == 'producer':
            task.cancel()
