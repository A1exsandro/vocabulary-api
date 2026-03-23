from app.application.ports.vocabulary_enricher import VocabularyEnricher
from app.integrations.openrouter_client import generate_sentences


class OpenRouterVocabularyEnricher(VocabularyEnricher):
    def enrich(self, text: str) -> dict:
        return generate_sentences(text)
