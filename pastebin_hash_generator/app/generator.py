import json
import secrets
import asyncio
from fastapi import HTTPException, status
from loguru import logger


async def generator_func(redis, count=50, waiting=60):
    """Generate some amount of hash every 60 seconds(changeable) and put it to Redis"""
    try:
        logger.info("Hash generation started")
        while True:
            for _ in range(count):
                hash_ = json.dumps(secrets.token_urlsafe(8))
                await redis.rpush("hash_redis_queue", hash_)
            await asyncio.sleep(waiting)
    except ConnectionError as error:
        logger.error(f"Redis error: {error}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error)
