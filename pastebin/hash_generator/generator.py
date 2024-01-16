import redis
import json
import os
import logging
import secrets
import random
from redis.exceptions import ConnectionError
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(level=logging.INFO)


class HashGenerator:
    def __init__(self):
        try:
            self.redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, decode_responses=False)
        except ConnectionError as error:
            logging.error(f'Error initializing HashGenerator: {error}')

    def start_generate(self):
        logging.info('Start generate...')
        for _ in range(5):
            hash_ = json.dumps(secrets.token_urlsafe(8))

            key = random.randrange(1, 10000)  # максимум возможных ключей в одно время

            try:
                self.redis_client.set(f':1:hash_key: {key}', hash_, ex=None)

            except ConnectionError as error:
                logging.error(f'Connection error: {error}')
                logging.info('Stop generate')
                break

        logging.info('Generating completed')


generator = HashGenerator()
