import os

from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


from meta.singleton import Singleton
from util.logger import get_logger


class PdfSelector(metaclass=Singleton):
    def __init__(self):
        self._examples: list = [
            # İŞÇİ KANUNU
            {"input": "İşçi hakları", "output": "is_isci_kanun"},
            {"input": "Kovulmak", "output": "is_isci_kanun"},
            {"input": "İş yeri", "output": "is_isci_kanun"},
            {"input": "İş sözleşmesi", "output": "is_isci_kanun"},
            {"input": "Kıdem tazminatı", "output": "is_isci_kanun"},
            {"input": "İhbar tazminatı", "output": "is_isci_kanun"},
            {"input": "Fazla mesai ücreti", "output": "is_isci_kanun"},
            {"input": "İş güvencesi", "output": "is_isci_kanun"},
            {"input": "Sendikal haklar", "output": "is_isci_kanun"},
            {"input": "İş kazası tazminatı", "output": "is_isci_kanun"},
            {"input": "Yıllık izin hakkı", "output": "is_isci_kanun"},
            {"input": "Asgari ücret", "output": "is_isci_kanun"},

            # BORÇLAR KANUNU
            {"input": "Borçlar hukuku", "output": "borclar_kanun"},
            {"input": "Müteselsil borç", "output": "borclar_kanun"},
            {"input": "Sözleşmeden doğan borçlar", "output": "borclar_kanun"},
            {"input": "Haksız fiil", "output": "borclar_kanun"},
            {"input": "Sebepsiz zenginleşme", "output": "borclar_kanun"},
            {"input": "Kira sözleşmesi", "output": "borclar_kanun"},
            {"input": "Kira artışı", "output": "borclar_kanun"},
            {"input": "Borçlu ve alacaklı hakları", "output": "borclar_kanun"},
            {"input": "Tazminat yükümlülükleri", "output": "borclar_kanun"},
            {"input": "Sorumluluk halleri", "output": "borclar_kanun"}
        ]
        self._logger = get_logger(__name__)
        self._example_selector = SemanticSimilarityExampleSelector.from_examples(
            self._examples,
            GoogleGenerativeAIEmbeddings(model="models/text-embedding-004",
                                         google_api_key=os.getenv("GEMINI_API_KEY")),
            InMemoryVectorStore,
            k=5
        )

    def _remove_duplicates(self, result: list[dict]) -> list[str]:
        unique_result = []
        for res in result:
            if "output" in res and res["output"] not in unique_result:
                unique_result.append(res["output"])
        return unique_result

    async def aselect(
            self,
            question: dict[str, str]
    ) -> list[str]:
        example_selector_results: list[dict] = await self._example_selector.aselect_examples(question)
        results: list[str] = self._remove_duplicates(example_selector_results)
        return results