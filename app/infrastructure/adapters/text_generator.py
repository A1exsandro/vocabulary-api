from app.application.ports.text_generator import TextGenerator
from app.integrations.openrouter_client import generate_short_text


class OpenRouterTextGenerator(TextGenerator):
    def generate(self, topic: str) -> dict:
        return generate_short_text(topic)
