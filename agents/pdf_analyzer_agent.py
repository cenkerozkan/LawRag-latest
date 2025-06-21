import os
import re
from dotenv import load_dotenv

from google import genai
from google.genai.types import GenerateContentResponse

from util.logger import get_logger
from util.prompt_generator import prompt_generator
from db.model.pdf_content_model import PdfContentModel

load_dotenv()

class PdfAnalyzerAgent:
    __slots__ = ("_gemini_client", "_logger")
    def __init__(self):
        self._logger = get_logger(__name__)
        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        except Exception as e:
            self._logger.error(f"Error initalizing PdfSelectorAgent: {e}")

    async def analyze_pdf(
            self,
            pdf_contents: list[PdfContentModel],
            conversation_history: list[dict],
            user_query: str
    ) -> list:
        prompt: str = prompt_generator.generate_pdf_analyzer_prompt(user_query, conversation_history, pdf_contents)
        response: GenerateContentResponse = None
        try:
            response = await self._gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt
            )
            self._logger.info(f"Pdf Analyzer Results: {response.text.strip()}")
        except Exception as e:
            self._logger.error(f"Error initalizing PdfSelectorAgent: {e}")

        if not response or not response.text or response.text == "false":
            return []
        xml_text = response.text.strip()

        selected_parts: list[str] = re.findall(r"<selected_parts>(.*?)</selected_parts>",
                          xml_text,
                          re.DOTALL | re.IGNORECASE)
        selected_parts = [part.strip() for part in selected_parts if part.strip()]
        return selected_parts

pdf_analyzer_agent = PdfAnalyzerAgent()