import os
from time import sleep
from dotenv import load_dotenv
from loguru import logger
from kafka import KafkaConsumer


load_dotenv()


class HashGenerator:
    def __init__(self):
        self.KAFKA_HOST = os.getenv("KAFKA_HOST")
        self.KAFKA_PORT = os.getenv("KAFKA_PORT")
        self.consumer = KafkaConsumer('hashes',
                                      bootstrap_servers=[f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"])

    def get_hash(self) -> str | None:
        hash_ = None
        for message in self.consumer:
            hash_ = message.value.decode()
            logger.info(f"Received hash from Kafka: {hash_}")
            break
        return hash_


hash_generator = HashGenerator()
