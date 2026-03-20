import os
import uuid
import io
from app.integrations.s3_client import s3_client
from app.integrations.pixabay_client import fetch_image_from_pixabay

S3_IMAGE_BUCKET_NAME = os.getenv("S3_IMAGE_BUCKET_NAME")

class ImageService:

    @staticmethod
    async def generate(word: str) -> str:

        image_bytes = fetch_image_from_pixabay(word)

        image_filename = f"{uuid.uuid4()}.jpg"

        buffer = io.BytesIO(image_bytes)

        s3_client.upload_fileobj(
            buffer,
            S3_IMAGE_BUCKET_NAME,
            image_filename,
            ExtraArgs={"ContentType": "image/jpeg"},
        )

        return image_filename
    