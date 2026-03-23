from abc import ABC, abstractmethod


class ImageGenerator(ABC):
    @abstractmethod
    async def generate(self, text: str) -> str:
        raise NotImplementedError
