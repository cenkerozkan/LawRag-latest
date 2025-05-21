import os
import re
from dotenv import load_dotenv

from google import genai
from util.logger import get_logger
from util.prompt_generator import prompt_generator

load_dotenv()

class PdfSelectorAgent:
    __slots__ = ("_gemini_client", "_logger")

    def __init__(self):
        self._logger = get_logger(__name__)
        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            self._logger.error(f"Error initializing PdfSelectorAgent: {e}")

    async def select_laws(
        self,
        query: str,
    ) -> list[str]:
        """
        Call Gemini with the PDF selector prompt and parse the returned XML to extract relevant laws.
        Returns a list of law keys (e.g. ["turk_ceza_kanun", "medeni_kanun"])
        """
        prompt = prompt_generator.generate_pdf_selector_prompt(query)
        response = None
        try:
            response = self._gemini_client.models.generate_content(
                model="gemma-3-27b-it",
                contents=prompt,
            )
            self._logger.info(f"PDF Selector Agent Gemini Output: {response.text}")
        except Exception as e:
            self._logger.error(f"Error generating PDF selector content: {e}")
            raise e

        # Parse <law>...</law> values between <relevant_laws>...</relevant_laws>
        law_keys: list = []
        if not response or not response.text:
            return []
        xml_text = response.text.strip()
        match = re.search(r"<relevant_laws>(.*?)</relevant_laws>", xml_text, re.DOTALL | re.IGNORECASE)
        if match:
            inner = match.group(1)
            law_keys = re.findall(r"<law>(.*?)</law>", inner, re.IGNORECASE)
        # Also support the case where no relevant laws found, e.g. <relevant_laws></relevant_laws>
        law_keys = [key.strip() for key in law_keys if key.strip()]
        return law_keys

pdf_selector_agent = PdfSelectorAgent()