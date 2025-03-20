from abc import ABC, abstractmethod
from util.embedding_model_getter import get_embedding_model

class DocumentRepositoryBase(ABC):
    def __init__(self):
        self._model = get_embedding_model("cohere-light")

    @abstractmethod
    async def aretrieve(self, query: str):
        raise NotImplementedError()