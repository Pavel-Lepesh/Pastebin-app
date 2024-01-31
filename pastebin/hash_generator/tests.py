from django.test import SimpleTestCase
import redis
import os
from dotenv import load_dotenv
from django.core.cache import caches

load_dotenv()


class HashGeneratorTests(SimpleTestCase):
    def test_connection_redis(self):
        redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379)
        self.assertTrue(redis_client.ping())

    def test_set_and_get_key_redis(self):
        redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379)
        redis_client.set(':1:hash_key: test', 123456789, ex=None)
        value = caches['redis'].get('hash_key: test')
        self.assertEqual(value, 123456789)

    def test_delete_hash_key_redis(self):
        caches['redis'].delete('hash_key: test')
        self.assertIsNone(caches['redis'].get('hash_key: test'))
