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

    async def generate_hyde_content(
            self,
            query: str,
            conversation_history: list[dict[str, str]],
            selected_pdfs: list[str]
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": ""
        }
        try:
            prompt: str = prompt_generator.generate_hyde_rag_search_prompt(
                query=query,
                conversation_history=conversation_history,
                selected_pdfs=selected_pdfs
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
                result.update({"success": True, "message": "HyDE content generated successfully",
                               "data": response.text.strip()})
            else:
                result.update({"success": False, "message": "No relevant HyDE content generated"})

        except Exception as e:
            self._logger.error(f"Error generating HyDE content: {e}")
            result.update({"success": False, "message": "Error generating HyDE content", "error": str(e)})

        return result


hyde_generator_agent = HyDEGeneratorAgent()