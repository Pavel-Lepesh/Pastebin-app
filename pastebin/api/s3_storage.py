import boto3
import uuid
from botocore.client import Config


ENDPOINT = "https://s3.ru-1.storage.selcloud.ru"

ACCESS_KEY = "8e74b075d0624260bbc60d1e34ad9068"
SECRET_KEY = "a4d25d1abdc4401ca7d2cf3d756a748e"

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
