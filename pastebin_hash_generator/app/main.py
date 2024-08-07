from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from redis import asyncio as aioredis
from redis import ConnectionError
from aiokafka import AIOKafkaProducer

from app.kafka_producer import producer_func
from app.generator import generator_func
from app.config import settings
from app.router import router as gen_router
from loguru import logger


logger.add(
    "log_file.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {file}:{line} | {message}",
    rotation="50 MB",
    level="INFO",
    enqueue=True
)

logger.add(
    "error_logs.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {file}:{line} | {message}",
    rotation="50 MB",
    level="ERROR",
    enqueue=True
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True,
        )
    try:
        await redis.ping()
        logger.info("Redis client is active")
    except ConnectionError as error:
        logger.error(f"Unable to connect to Redis client: {error}")

    kafka_client = AIOKafkaProducer(bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}", acks=1)
    task_generator = asyncio.create_task(generator_func(redis=redis), name='hash_generator')
    task_producer = asyncio.create_task(producer_func(redis=redis, kafka_client=kafka_client), name='producer')
    yield
    await redis.close()


app = FastAPI(lifespan=lifespan)
app_v1 = FastAPI()

app_v1.include_router(gen_router)
app.mount("/v1", app_v1)
