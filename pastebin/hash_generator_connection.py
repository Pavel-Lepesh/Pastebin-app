import logging
import os
from time import sleep

import pika
from dotenv import load_dotenv
from pika.exceptions import AMQPError

load_dotenv()
logger = logging.getLogger(__name__)


class HashGenerator:
    def __init__(self):
        try:
            self.channel = self.connection_to_rabbit()
            logger.info(f"RabbitMQ is connected")
        except AMQPError as error:
            logger.error(f"Error connection RabbitMQ: {error}")

    def get_hash(self) -> str | None:
        response = self.channel.basic_get('HashQueue', auto_ack=True)
        hash_: str | None = response[2].decode().strip('"') if response[2] else None
        return hash_

    @staticmethod
    def connection_to_rabbit(wait=3, retries=5):
        attempt = 0
        while attempt < retries:
            try:
                credentials = pika.PlainCredentials(os.getenv("RABBITMQ_USER"), os.getenv("RABBITMQ_PASSWORD"))
                parameters = pika.ConnectionParameters(os.getenv("RABBITMQ_HOST"),
                                                       os.getenv("RABBITMQ_PORT"),
                                                       os.getenv("RABBITMQ_VIRTUAL_HOST"),
                                                       credentials)
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                return channel
            except AMQPError as error:
                logger.warning(f"Attempt connection to RabbitMQ №{attempt} was failed")
                attempt += 1
                sleep(wait)
        else:
            logger.error("Error connection RabbitMQ")


hash_generator = HashGenerator()
