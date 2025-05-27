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
    ) -> str:
        self._logger.info(f"Generating HyDE for query: {query}")
        hyde_result = await hyde_generator_agent.generate_hyde_content(
            query=query,
            conversation_history=conversation_history,
            law_name=law_name
        )
        hyde_data: str = hyde_result.get("data", "")
        if hyde_data == "false":
            self._logger.warn(f"HyDE generation returned false for query: {query}")
            return query
        if len(hyde_data) == 0:
            self._logger.warn(f"No HyDE content generated for query: {query}")
            return query
        else:
            self._logger.info(f"HyDE content generated successfully for query: {query}")
            return hyde_data


    # NOTE: Buraya istemediğim bir bağımlılık ekliyorum.
    @abstractmethod
    async def aretrieve(
            self,
            query: str,
            conversation_history: list,
    ) -> str:
        raise NotImplementedError()