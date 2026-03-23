from abc import ABC, abstractmethod


class AudioGenerator(ABC):
    @abstractmethod
    async def generate(self, text: str) -> str:
        raise NotImplementedError
