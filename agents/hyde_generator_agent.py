import re
import os
from dotenv import load_dotenv

from google import genai
from util.logger import get_logger
from util.prompt_generator import prompt_generator

load_dotenv()


class HyDEGeneratorAgent:
    __slots__ = ("_gemini_client", "_logger")

    def __init__(self):
        self._logger = get_logger(__name__)
        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            self._logger.error(f"Error initializing HyDEGeneratorAgent: {e}")

    def _parse_hyde_content(self, response_text: str) -> list[str]:
        """
        Parse <hyde>...</hyde> tags from the response text and return them as a list of strings.
        Returns a list of HyDE content strings.
        """
        hyde_contents: list = []
        if not response_text:
            return []

        # Find all <hyde>...</hyde> tags in the response
        hyde_matches = re.findall(r"<hyde>(.*?)</hyde>", response_text, re.DOTALL | re.IGNORECASE)

        # Clean up and filter the content
        hyde_contents = [content.strip() for content in hyde_matches if content.strip()]

        self._logger.info(f"Found {len(hyde_contents)} HyDE contents in response")
        return hyde_contents

    async def generate_hyde_content(
            self,
            query: str,
            conversation_history: list[dict[str, str]],
            law_name: str
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        try:
            prompt: str = prompt_generator.generate_hyde_rag_search_prompt(
                query=query,
                conversation_history=conversation_history,
                law_name=law_name
            )
            self._logger.info(f"Generating HyDE content for query: {query}")

            response = self._gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            if response.text.strip():
                if response.text.strip() == "false":
                    result.update({"success": False, "message": "HyDE content generation returned false"})
                    self._logger.error(f"HyDE content generation returned false: {query}")
                    return result

                # Parse <hyde>...</hyde> values
                hyde_contents: list[str] = self._parse_hyde_content(response.text.strip())
                hyde_contents_str: str = "".join(hyde_contents)

                if hyde_contents:
                    result.update({
                        "success": True,
                        "message": "HyDE content generated successfully",
                        "data": {"hyde_contents": hyde_contents}
                    })
                    self._logger.info(f"Parsed {len(hyde_contents)} HyDE contents")
                else:
                    result.update({"success": False, "message": "No valid HyDE content found in response"})
            else:
                result.update({"success": False, "message": "No relevant HyDE content generated"})

        except Exception as e:
            self._logger.error(f"Error generating HyDE content: {e}")
            result.update({"success": False, "message": "Error generating HyDE content", "error": str(e)})

        return result

hyde_generator_agent = HyDEGeneratorAgent()