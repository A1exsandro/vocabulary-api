import os
import io
import uuid
from gtts import gTTS
from app.integrations.s3_client import s3_client

S3_AUDIO_BUCKET_NAME = os.getenv("S3_AUDIO_BUCKET_NAME")

class AudioService:

    @staticmethod
    async def generate(word: str) -> str:

        mp3_buffer = io.BytesIO()

        tts = gTTS(text=word, lang="en")
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        audio_filename = f"{uuid.uuid4()}.mp3"

        s3_client.upload_fileobj(
            mp3_buffer,
            S3_AUDIO_BUCKET_NAME,
            audio_filename,
            ExtraArgs={"ContentType": "audio/mpeg"},
        )

        return audio_filename
    