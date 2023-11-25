import random
import base64
import time
import redis
import json
import logging


logging.basicConfig(level=logging.INFO)


class HashGenerator:
    def __init__(self):
        logging.info('Start generate...')
        self.count = 0
        self.hashes = set()
        self.redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=False)

        self.start_generate()

    def start_generate(self):
        while True:
            hash_ = json.dumps(HashGenerator.generate_hash())
            if hash_ in self.hashes:
                continue

            self.hashes.add(hash_)
            logging.info(f'New hash: {hash_}')
            key = f":1:{self.count}"

            self.redis_client.set(key, hash_, ex=None)
            time.sleep(2)

            self.count += 1

    @staticmethod
    def generate_hash():
        digit = str(random.randrange(1_000_000_000, 10_000_000_000))
        return base64.b64encode(bytes(digit, 'utf-8')).decode('utf-8')


if __name__ == '__main__':
    hash_generator = HashGenerator()
