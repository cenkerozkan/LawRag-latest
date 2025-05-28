from abc import ABC, abstractmethod
from util.logger import get_logger
from util.prompt_generator import PromptGenerator
from agents.hyde_generator_agent import hyde_generator_agent

class DocumentRepositoryBase(ABC):
    _logger = get_logger(__name__)

    def __init__(self):
        pass

    async def _generate_hyde(
            self,
            query: str,
            conversation_history: list,
            law_name: str
    ) -> list[str]:
        self._logger.info(f"Generating HyDE for query: {query}")
        hyde_result: dict = await hyde_generator_agent.generate_hyde_content(
            query=query,
            conversation_history=conversation_history,
            law_name=law_name
        )
        if not hyde_result.get("success"):
            self._logger.warn(f"No HyDE content generated for query: {query}")
            return [query]
        if hyde_result.get("hyde_contents") == "false":
            self._logger.warn(f"No HyDE content generated for query: {query}")
            return [query]
        else:
            return hyde_result.get("data").get("hyde_contents")

    # NOTE: Buraya istemediğim bir bağımlılık ekliyorum.
    @abstractmethod
    async def aretrieve(
            self,
            query: str,
            conversation_history: list,
    ) -> str:
        raise NotImplementedError()