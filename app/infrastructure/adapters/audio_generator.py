from app.application.ports.audio_generator import AudioGenerator
from app.services.audio_service import AudioService


class GttsAudioGenerator(AudioGenerator):
    async def generate(self, text: str) -> str:
        return await AudioService.generate(text)
