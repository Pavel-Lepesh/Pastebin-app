import os

from dotenv import load_dotenv
from kafka import KafkaProducer
from loguru import logger

load_dotenv()


class KafkaProducerClient:
    def __init__(self):
        self.host = os.getenv("KAFKA_HOST")
        self.port = os.getenv("KAFKA_PORT")

    def send_note(self, title, hash_link):
        producer: KafkaProducer = KafkaProducer(bootstrap_servers=[f"{self.host}:{self.port}"])
        if not producer.bootstrap_connected():
            logger.error("Kafka client is not active")
        else:
            producer.send('notes-1', key=b'documents', value=f"{hash_link}{title}".encode())
            logger.info(f"Note \"{title}\" sent to Kafka")


kafka_producer = KafkaProducerClient()
