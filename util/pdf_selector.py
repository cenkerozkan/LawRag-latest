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
            {"input": "tazminatsız", "output": "is_isci_kanun"},
            {"input": "fazla mesai", "output": "is_isci_kanun"},
            {"input": "yıllık izin", "output": "is_isci_kanun"},
            {"input": "iş kazası", "output": "is_isci_kanun"},
            {"input": "sendika", "output": "is_isci_kanun"},
            {"input": "kıdem tazminatı", "output": "is_isci_kanun"},
            {"input": "ihbar süresi", "output": "is_isci_kanun"},
            {"input": "doğum izni", "output": "is_isci_kanun"},
            {"input": "hafta tatili", "output": "is_isci_kanun"},
            {"input": "iş sözleşmesi", "output": "is_isci_kanun"},

            # BORÇLAR KANUNU
            {"input": "kira sözleşmesi", "output": "borclar_kanun"},
            {"input": "borçlu", "output": "borclar_kanun"},
            {"input": "haksız fiil", "output": "borclar_kanun"},
            {"input": "sebepsiz zenginleşme", "output": "borclar_kanun"},
            {"input": "cezai şart", "output": "borclar_kanun"},
            {"input": "müteselsil borç", "output": "borclar_kanun"},
            {"input": "kira artış", "output": "borclar_kanun"},
            {"input": "alacaklı", "output": "borclar_kanun"},
            {"input": "sözleşme feshi", "output": "borclar_kanun"},
            {"input": "temerrüt faizi", "output": "borclar_kanun"},

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