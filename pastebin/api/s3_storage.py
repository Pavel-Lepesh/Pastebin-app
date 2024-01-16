import boto3
import os
from datetime import datetime
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv


load_dotenv()


class S3Storage:
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
                        region_name="ru-1"
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

        self.client.put_object(Bucket=self.BUCKET_NAME,
                               Key=key_for_s3,
                               Body=f'{content}',
                               Expires=ex)

    def delete_object(self, key_for_s3):
        self.client.delete_object(Bucket=self.BUCKET_NAME, Key=key_for_s3)


s3_storage = S3Storage()
