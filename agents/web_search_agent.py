import os
from dotenv import load_dotenv

from google import genai
from util.logger import get_logger
from util.prompt_generator import PromptGenerator
from util.google_search import google_search

load_dotenv()

class WebSearchAgent:
    __slots__ = ("_gemini_client","_logger")
    def __init__(self):
        self._logger = get_logger(__name__)
        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            self._logger.error(f"Error initializing WebSearchAgent: {e}")

    async def search_web(
            self,
            query: str,
            conversation_history: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        prompt: str = PromptGenerator.generate_web_search_prompt(query, conversation_history)
        response: any
        results: list[dict[str, str]] = []

        try:
            response = self._gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            self._logger.info(f"Web search query by Agent: {query}")
        except Exception as e:
            self._logger.error(f"Error generating web search content: {e}")
            return []

        _ = await google_search(response.text)
        results = [result for result in _]
        return results

web_search_agent = WebSearchAgent()