import os
import boto3
from botocore.client import Config

# ENV
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_AUDIO_BUCKET_NAME = os.getenv("S3_AUDIO_BUCKET_NAME")
S3_IMAGE_BUCKET_NAME = os.getenv("S3_IMAGE_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")
S3_PUBLIC_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
    config=Config(signature_version="s3v4"),
)

# Cliente público (para gerar URLs acessíveis pelo browser)
s3_public = boto3.client(
    "s3",
    endpoint_url=S3_PUBLIC_ENDPOINT,
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    region_name=os.getenv("S3_REGION"),
)