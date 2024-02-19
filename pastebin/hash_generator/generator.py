import redis
import json
import os
import logging
import secrets
import random
from redis.exceptions import ConnectionError
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


class HashGenerator:
    def __init__(self):
        try:
            self.redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, decode_responses=False)
        except ConnectionError as error:
            logger.error(f'Error initializing HashGenerator: {error}')

    def start_generate(self, hash_count=50):
        logger.info('Start generate')
        for _ in range(hash_count):
            hash_ = json.dumps(secrets.token_urlsafe(8))

            key = random.randrange(1, 10000)  # максимум возможных ключей в одно время

            try:
                self.redis_client.set(f':1:hash_key: {key}', hash_, ex=None)

            except ConnectionError as error:
                logger.error(f'Connection error: {error}')
                logger.info('Stop generate')
                break

        logging.info('Generating completed')


generator = HashGenerator()
