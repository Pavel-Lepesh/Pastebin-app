from kafka import KafkaProducer
from dotenv import load_dotenv
import os
from loguru import logger


load_dotenv()


class KafkaProducerClient:
    def __init__(self):
        self.host = os.getenv("KAFKA_HOST")
        self.port = os.getenv("KAFKA_PORT")
        self.producer: KafkaProducer = KafkaProducer(bootstrap_servers=[f"{self.host}:{self.port}"])

    def send_note(self, title, hash_link):
        if not self.producer.bootstrap_connected():
            logger.error("Kafka client is not active")
        else:
            self.producer.send('notes-1', key=b'documents', value=f"{hash_link}{title}".encode())
            logger.info(f"Note \"{title}\" sent to Kafka")


kafka_producer = KafkaProducerClient()
