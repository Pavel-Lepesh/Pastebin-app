import redis
import json
import logging
import secrets
import random
from redis.exceptions import ConnectionError


logging.basicConfig(level=logging.INFO)


class HashGenerator:
    def __init__(self):
        logging.info('Start generate...')
        self.redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=False)

        self.start_generate()

    def start_generate(self):
        for _ in range(50):
            hash_ = json.dumps(secrets.token_urlsafe(8))

            key = random.randrange(1, 10000)  # максимум возможных ключей в одно время

            try:
                self.redis_client.set(f':1:hash_key: {key}', hash_, ex=None)

            except ConnectionError as error:
                logging.error(f'Connection error: {error}')
                logging.info('Stop generate')
                break

            logging.info(f'New hash: {hash_}')
