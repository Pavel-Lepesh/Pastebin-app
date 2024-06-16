import json
import secrets
import asyncio
from fastapi import HTTPException, status


async def generator_func(redis, count=50, waiting=60):
    try:
        while True:
            for _ in range(count):
                hash_ = json.dumps(secrets.token_urlsafe(8))
                await redis.rpush("hash_redis_queue", hash_)
            await asyncio.sleep(waiting)
    except ConnectionError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error)
