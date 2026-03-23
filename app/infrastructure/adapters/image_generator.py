from app.application.ports.image_generator import ImageGenerator
from app.services.image_service import ImageService


class PixabayImageGenerator(ImageGenerator):
    async def generate(self, text: str) -> str:
        return await ImageService.generate(text)
