import os

from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_cohere import CohereEmbeddings


from meta.singleton import Singleton
from util.logger import get_logger
from util.embedding_model_getter import get_embedding_model
from agents.pdf_selector_agent import pdf_selector_agent


class PdfSelector(metaclass=Singleton):
    def __init__(self):
        self._model = get_embedding_model("cohere-light")
        self._examples: list = [

            # İŞÇİ KANUNU
            {"input": "İşçi hakları", "output": "is_isci_kanun"},
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
            {"input": "Sorumluluk halleri", "output": "borclar_kanun"},

            # SİNAİ MÜLKİYET KANUNU
            {"input": "marka tescili", "output": "sinai_mulkiyet_kanun"},
            {"input": "patent", "output": "sinai_mulkiyet_kanun"},
            {"input": "faydalı model", "output": "sinai_mulkiyet_kanun"},
            {"input": "tasarım tescili", "output": "sinai_mulkiyet_kanun"},
            {"input": "marka ihlali", "output": "sinai_mulkiyet_kanun"},
            {"input": "coğrafi işaret", "output": "sinai_mulkiyet_kanun"},
            {"input": "lisans sözleşmesi", "output": "sinai_mulkiyet_kanun"},
            {"input": "teknoloji transferi", "output": "sinai_mulkiyet_kanun"},

            # TÜRK CEZA KANUNU
            {"input": "kasten öldürme", "output": "turk_ceza_kanun"},
            {"input": "taksirle yaralama", "output": "turk_ceza_kanun"},
            {"input": "cinsel saldırı", "output": "turk_ceza_kanun"},
            {"input": "dolandırıcılık", "output": "turk_ceza_kanun"},
            {"input": "hakaret", "output": "turk_ceza_kanun"},
            {"input": "uyuşturucu", "output": "turk_ceza_kanun"},
            {"input": "zimmet", "output": "turk_ceza_kanun"},
            {"input": "rüşvet", "output": "turk_ceza_kanun"},
            {"input": "meşru müdafaa", "output": "turk_ceza_kanun"},
            {"input": "ceza indirimi", "output": "turk_ceza_kanun"},

            # CEZA MUHAKEMESİ KANUNU
            {"input": "tutuklama", "output": "ceza_muhakeme_kanun"},
            {"input": "gözaltı", "output": "ceza_muhakeme_kanun"},
            {"input": "soruşturma", "output": "ceza_muhakeme_kanun"},
            {"input": "delil toplama", "output": "ceza_muhakeme_kanun"},
            {"input": "savcılık", "output": "ceza_muhakeme_kanun"},
            {"input": "adli kontrol", "output": "ceza_muhakeme_kanun"},
            {"input": "iddianame", "output": "ceza_muhakeme_kanun"},
            {"input": "şüpheli", "output": "ceza_muhakeme_kanun"},
            {"input": "arama", "output": "ceza_muhakeme_kanun"},
            {"input": "tanık koruma", "output": "ceza_muhakeme_kanun"},

            # ELEKTRONİK TİCARETİN DÜZENLENMESİ HAKKINDA KANUN
            {"input": "ticari ileti", "output": "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun"},
            {"input": "e-posta", "output": "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun"},
            {"input": "SMS", "output": "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun"},
            {"input": "e-ticaret", "output": "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun"},
            {"input": "reklam", "output": "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun"},
            {"input": "abonelik", "output": "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun"},
            {"input": "tüketici hakları", "output": "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun"},

            # GELİR VERGİSİ KANUNU
            {"input": "gelir vergisi", "output": "gelir_vergisi_kanunu"},
            {"input": "vergi dilimi", "output": "gelir_vergisi_kanunu"},
            {"input": "serbest meslek", "output": "gelir_vergisi_kanunu"},
            {"input": "kira geliri", "output": "gelir_vergisi_kanunu"},
            {"input": "vergi indirimi", "output": "gelir_vergisi_kanunu"},
            {"input": "vergi cezası", "output": "gelir_vergisi_kanunu"},

            # İNFAZ KANUNU
            {"input": "hapis cezası", "output": "infaz_kanun"},
            {"input": "şartlı tahliye", "output": "infaz_kanun"},
            {"input": "denetimli serbestlik", "output": "infaz_kanun"},
            {"input": "açık cezaevi", "output": "infaz_kanun"},
            {"input": "infaz erteleme", "output": "infaz_kanun"},

            # KİŞİSEL VERİLERİN KORUNMASI KANUNU
            {"input": "kişisel veri", "output": "kvkk_kanun"},
            {"input": "veri ihlali", "output": "kvkk_kanun"},
            {"input": "aydınlatma yükümlülüğü", "output": "kvkk_kanun"},
            {"input": "açık rıza", "output": "kvkk_kanun"},
            {"input": "veri sorumlusu", "output": "kvkk_kanun"},
            {"input": "veri güvenliği", "output": "kvkk_kanun"},

            # MEDENİ KANUN
            {"input": "boşanma", "output": "medeni_kanun"},
            {"input": "nafaka", "output": "medeni_kanun"},
            {"input": "velayet", "output": "medeni_kanun"},
            {"input": "mal rejimi", "output": "medeni_kanun"},
            {"input": "evlat edinme", "output": "medeni_kanun"},
            {"input": "nişan", "output": "medeni_kanun"},
            {"input": "aile konutu", "output": "medeni_kanun"},
            {"input": "vasiyetname", "output": "medeni_kanun"},

            # REKABETİN KORUNMASI HAKKINDA KANUN
            {"input": "tekel", "output": "rekabet_kanun"},
            {"input": "haksız rekabet", "output": "rekabet_kanun"},
            {"input": "rekabet kurumu", "output": "rekabet_kanun"},
            {"input": "birleşme", "output": "rekabet_kanun"},
            {"input": "ihale", "output": "rekabet_kanun"},
            {"input": "rekabet yasağı", "output": "rekabet_kanun"},

            # TÜKETİCİNİN KORUNMASI HAKKINDA KANUN
            {"input": "iade", "output": "tuketici_kanun"},
            {"input": "garanti", "output": "tuketici_kanun"},
            {"input": "ayıplı mal", "output": "tuketici_kanun"},
            {"input": "kapıdan satış", "output": "tuketici_kanun"},
            {"input": "taksitli satış", "output": "tuketici_kanun"},
            {"input": "tüketici hakem heyeti", "output": "tuketici_kanun"},

            # TÜRK TİCARET KANUNU
            {"input": "şirket türleri", "output": "turk_ticaret_kanun"},
            {"input": "anonim şirket", "output": "turk_ticaret_kanun"},
            {"input": "limited şirket", "output": "turk_ticaret_kanun"},
            {"input": "ticari işletme", "output": "turk_ticaret_kanun"},
            {"input": "ticari senet", "output": "turk_ticaret_kanun"},
            {"input": "iflas", "output": "turk_ticaret_kanun"},

            # VERGİ USUL KANUNU
            {"input": "fatura", "output": "vergi_usul_kanun"},
            {"input": "vergi mükellefiyeti", "output": "vergi_usul_kanun"},
            {"input": "beyanname", "output": "vergi_usul_kanun"},
            {"input": "vergi ziyaı", "output": "vergi_usul_kanun"},
            {"input": "usulsüzlük", "output": "vergi_usul_kanun"},
            {"input": "vergi incelemesi", "output": "vergi_usul_kanun"},
        ]
        self._logger = get_logger(__name__)
        self._example_selector = SemanticSimilarityExampleSelector.from_examples(
            self._examples,
            CohereEmbeddings(model=self._model),
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

    async def aselect_with_agent(
            self,
            query: str
    ) -> list[str]:
        """
        Use the PDF Selector Agent (Gemini LLM) for law selection.
        Falls back to old selector if agent fails.
        """
        try:
            law_keys = await pdf_selector_agent.select_laws(query)
            return law_keys
        except Exception as e:
            self._logger.error(f"PDF Selector Agent failed, falling back to legacy selector: {e}")
            # Fallback to legacy selector with same output format
            return await self.aselect({"input": query})