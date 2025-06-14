import os
import re

from google import genai
from dotenv import load_dotenv

from util.logger import get_logger
from util.prompt_generator import prompt_generator

load_dotenv()

class ChatNameGeneratorAgent():
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__)
        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            self._logger.error(f"An error occured: {e}")

    def _parse_chat_title(
            self,
            gemini_response: str,
            default: str = "Yeni Sohbet"
    ) -> str:
        if not gemini_response:
            return default

        match = re.search(
            r"<title>\s*(.*?)\s*</title>",  # non-greedy capture between tags
            gemini_response,
            flags=re.IGNORECASE | re.DOTALL
        )

        return match.group(1).strip() if match else default

    async def generate_chat_name(
            self,
            user_query: str
    ) -> str | None:
        prompt: str = prompt_generator.generate_chat_title_prompt(user_query)

        try:
            response = await self._gemini_client.aio.models.generate_content(
                model="gemma-3-27b-it",
                contents=prompt,
            )
            self._logger.info(f"PDF Selector Agent Gemini Output: {response.text}")
        except Exception as e:
            self._logger.error(f"Error generating PDF selector content: {e}")
            return "New Chat"

        result: str = self._parse_chat_title(response.text.strip())
        return result

chat_name_generator_agent = ChatNameGeneratorAgent()