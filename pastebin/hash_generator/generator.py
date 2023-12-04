import redis
import json
import logging
import secrets
from redis.exceptions import ConnectionError


logging.basicConfig(level=logging.INFO)


class HashGenerator:
    def __init__(self):
        logging.info('Start generate...')
        self.count = 0
        self.redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=False)

        self.start_generate()

    def start_generate(self):
        for _ in range(10):
            hash_ = json.dumps(secrets.token_urlsafe(8))

            key = f":1:{self.count}"

            try:
                self.redis_client.set(f':1:hash_key: {key}', hash_, ex=None)

            except ConnectionError as error:
                logging.error(f'Connection error: {error}')
                logging.info('Stop generate')
                break

            logging.info(f'New hash: {hash_}')

            self.count += 1

    # def start_generate(self):
    #     while True:
    #         hash_ = json.dumps(secrets.token_urlsafe(8))
    #
    #         key = f":1:{self.count}"
    #
    #         try:
    #             self.redis_client.set(key, hash_, ex=None)
    #             self.redis_deck.rpush('hash_deck', self.count)
    #         except ConnectionError as error:
    #             logging.error(f'Connection error: {error}')
    #             logging.info('Stop generate')
    #             break
    #
    #         time.sleep(2)
    #         logging.info(f'New hash: {hash_}')
    #
    #         self.count += 1
