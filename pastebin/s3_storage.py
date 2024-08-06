import logging
import os
from datetime import datetime

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class S3Storage:
    """
    Class for connection S3-type storage. Allows you to put objects into buckets,
    check if an object exists, and remove objects from buckets.
    """
    def __init__(self):
        self.ENDPOINT = os.getenv('ENDPOINT')
        self.ACCESS_KEY = os.getenv('ACCESS_KEY')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.BUCKET_NAME = os.getenv('BUCKET_NAME')
        self.client = boto3.client(
                        "s3",
                        endpoint_url=self.ENDPOINT,
                        config=Config(signature_version="s3v4"),
                        aws_access_key_id=self.ACCESS_KEY,
                        aws_secret_access_key=self.SECRET_KEY,
                        # region optional
                        )

    def generate_link(self, key_for_s3, expiration=3600):
        presigned_url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.BUCKET_NAME, "Key": key_for_s3},
            ExpiresIn=expiration,
        )

        return presigned_url

    def object_exist(self, key_for_s3):
        try:
            self.client.head_object(Bucket=self.BUCKET_NAME, Key=key_for_s3)
            return True
        except ClientError:
            # if objects doesn't exist, return false response
            return False

    def get_object_content(self, key_for_s3):
        obj = self.client.get_object(Bucket=self.BUCKET_NAME, Key=key_for_s3)
        return obj['Body'].read().decode('utf-8')

    def create_or_update_object(self, content, key_for_s3, ex: datetime):
        if not content:
            content = self.get_object_content(key_for_s3)

        params = {'Bucket': self.BUCKET_NAME,
                  'Key': key_for_s3,
                  'Body': f'{content}'}

        if ex:
            params['Expires'] = ex

        self.client.put_object(**params)

    def delete_object(self, key_for_s3: str):
        self.client.delete_object(Bucket=self.BUCKET_NAME, Key=key_for_s3)

    def check_connection(self):
        try:
            logger.info("Check S3 connection")
            result = True if self.client.list_buckets() else False
            if result:
                logger.info("S3 connected successfully")
            else:
                logger.error("Error with connection to S3")
            return result
        except Exception as error:
            return False


s3_storage = S3Storage()
s3_storage.check_connection()
