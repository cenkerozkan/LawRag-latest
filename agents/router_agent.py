import os
import re
from dotenv import load_dotenv

from openai import AsyncClient

from util.logger import get_logger
from util.prompt_generator import prompt_generator
from db.model.chat_thread_model import ChatThreadModel
from config.config import MESSAGE_HISTORY_SIZE

load_dotenv()
_DECISION_RE = re.compile(r"<decision>\s*(rag|chat_agent)\s*</decision>", re.I)

class RouterAgent:
    __slots__ = ("_openai_client", "_logger")
    def __init__(self):
        self._logger = get_logger(__name__)
        self._openai_client = AsyncClient(api_key=os.getenv("OPENAI_API_KEY"))

    async def run(
            self,
            chat_thread: ChatThreadModel,
            user_query: str
    ) -> str:
        # Fetch contents (context history or message history you can say).
        contents: list = [{"role": "assistant" if msg.role == "ai" else "user", "content": msg.content} for msg in
                          chat_thread.history[-MESSAGE_HISTORY_SIZE:]]
        prompt: str = prompt_generator.generate_router_agent_prompt(user_query)
        contents.append({"role": "system", "content": prompt})
        response: str

        try:
            openai_response: any = await self._openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=contents
            )
            response = openai_response.choices[0].message.content
        except Exception as e:
            self._logger.error(f"Error During Generation: {e}")
            return "rag"

        match: any = _DECISION_RE.search(response or "rag")
        decision: str = match.group(1).lower() if match else "rag"
        self._logger.info(f"Decision: {decision}")

        return decision

router_agent = RouterAgent()