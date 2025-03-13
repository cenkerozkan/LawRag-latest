import os

from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


from meta.singleton import Singleton
from util.logger import get_logger


class PdfSelector(metaclass=Singleton):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._examples: list = [
            {"input": "İşçi hakları nelerdir?", "output": "is_isci_kanun"},
            {"input": "İşten çıkarılma durumunda işçinin hakları nelerdir?", "output": "is_isci_kanun"},
            {"input": "İşçi maaşları nasıl belirlenir?", "output": "is_isci_kanun"},
            {"input": "İşçi sendikalarının görevleri nelerdir?", "output": "is_isci_kanun"},
            {"input": "İş kazası durumunda işçinin hakları nelerdir?", "output": "is_isci_kanun"},
            {"input": "İşçi izin hakları nelerdir?", "output": "is_isci_kanun"},
            {"input": "İşçi tazminat hakları nelerdir?", "output": "is_isci_kanun"},
            {"input": "İşçi çalışma saatleri nasıl düzenlenir?", "output": "is_isci_kanun"},
            {"input": "İşçi sendikalarına üye olma hakkı var mı?", "output": "is_isci_kanun"},
            {"input": "İşçi grev hakkı nedir?", "output": "is_isci_kanun"},
            {"input": "borclar_kanunnda kira sözleşmeleri nasıl düzenlenir?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda alacaklı ve borçlu hakları nelerdir?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda temerrüt nedir?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda kefalet nasıl düzenlenir?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda sözleşme feshi nasıl yapılır?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda tazminat nasıl hesaplanır?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda zamanaşımı süreleri nelerdir?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda haksız fiil nedir?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda müteselsil borçluluk nedir?", "output": "borclar_kanun"},
            {"input": "borclar_kanunnda kira artışı nasıl yapılır?", "output": "borclar_kanun"}
        ]
        self._example_selector = SemanticSimilarityExampleSelector.from_examples(
            self._examples,
            GoogleGenerativeAIEmbeddings(model="models/text-embedding-004",
                                         google_api_key=os.getenv("GEMINI_API_KEY")),
            InMemoryVectorStore,
            k=2
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