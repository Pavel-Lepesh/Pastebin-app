import asyncio


async def producer_func(redis, connection):
    channel = connection.channel()
    qu = channel.queue_declare(queue='HashQueue', durable=True, arguments={'x-max-length': 100})
    channel.exchange_declare(exchange='HashExchange', exchange_type="direct", durable=True)
    channel.queue_bind(exchange='HashExchange', queue='HashQueue')
    await asyncio.sleep(1)
    while True:
        message_count = qu.method.message_count
        hashes = await redis.lpop("hash_redis_queue", count=10)
        if hashes and message_count < 100:
            for hash_ in hashes:
                channel.basic_publish(exchange="", routing_key='HashQueue', body=hash_)
        else:
            await asyncio.sleep(10)