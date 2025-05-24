from abc import ABC, abstractmethod
from util.logger import get_logger

class DocumentRepositoryBase(ABC):
    _logger = get_logger(__name__)

    def __init__(self):
        pass

    @abstractmethod
    async def aretrieve(self, query: str) -> str:
        raise NotImplementedError()