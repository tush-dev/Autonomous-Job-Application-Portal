import boto3
from botocore.config import Config
from typing import BinaryIO

from app.core.config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name=settings.S3_REGION,
    config=Config(signature_version="s3v4"),
)


async def upload_file(
    bucket: str,
    key: str,
    file: BinaryIO,
    content_type: str,
) -> str:
    s3_client.upload_fileobj(
        file,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return f"{settings.S3_ENDPOINT}/{bucket}/{key}"


async def get_presigned_url(
    bucket: str,
    key: str,
    expires_in: int = 3600,
) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


async def delete_file(bucket: str, key: str):
    s3_client.delete_object(Bucket=bucket, Key=key)
