from abc import ABC, abstractmethod


class VocabularyEnricher(ABC):
    @abstractmethod
    def enrich(self, text: str) -> dict:
        raise NotImplementedError
