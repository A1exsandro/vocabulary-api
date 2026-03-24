from app.application.ports.audio_generator import AudioGenerator
from app.application.ports.image_generator import ImageGenerator
from app.application.ports.text_generator import TextGenerator
from app.application.ports.vocabulary_enricher import VocabularyEnricher
from app.infrastructure.adapters.audio_generator import GttsAudioGenerator
from app.infrastructure.adapters.image_generator import PixabayImageGenerator
from app.infrastructure.adapters.text_generator import OpenRouterTextGenerator
from app.infrastructure.adapters.vocabulary_enricher import OpenRouterVocabularyEnricher


def get_vocabulary_enricher() -> VocabularyEnricher:
    return OpenRouterVocabularyEnricher()


def get_audio_generator() -> AudioGenerator:
    return GttsAudioGenerator()


def get_image_generator() -> ImageGenerator:
    return PixabayImageGenerator()


def get_text_generator() -> TextGenerator:
    return OpenRouterTextGenerator()
