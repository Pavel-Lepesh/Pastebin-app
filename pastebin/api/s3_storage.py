import boto3
import uuid
from botocore.client import Config
import os
from dotenv import load_dotenv

load_dotenv()


ENDPOINT = "https://s3.ru-1.storage.selcloud.ru"

ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name="ru-1",
    )

s3 = session.client(
    "s3", endpoint_url=ENDPOINT, config=Config(signature_version="s3v4")
    )


def generate_link(content, expiration=3600):
    object_name = str(uuid.uuid4())
    s3.put_object(Bucket="lepeshnotes", Key=object_name, Body=f'{content}')

    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": "lepeshnotes", "Key": object_name},
        ExpiresIn=expiration,
    )

    return presigned_url
