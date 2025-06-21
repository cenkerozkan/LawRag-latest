import datetime
import os
import traceback

from google import genai

# DOC REPOS.
from repository.hukuk_muhakemeleri_kanun_document_repository import HukukMuhakemeleriKanunDocumentRepository  # DEFAULT
from repository.icra_ve_iflas_kanun_document_repository import IcraVeIflasKanunDocumentRepository   # DEFAULT
from repository.idari_yargilama_usulu_kanun_document_repository import IdariYargilamaUsuluKanunDocumentRepository # DEFAULT
from repository.turk_anayasasi_document_repository import TurkAnayasasiDocumentRepository # DEFAULT
from repository.is_isci_kanun_document_repository import IsIsciKanunDocumentRepository
from repository.borclar_kanun_document_repository import BorclarKanunDocumentRepository
from repository.sinai_mulkiyet_kanun_document_repository import SinaiMulkiyetKanunDocumentRepository
from repository.turk_ceza_kanun_document_repository import TurkCezaKanunDocumentRepository
from repository.rekabetin_korunmasi_kanun_document_repository import RekabetinKorunmasiKanunDocumentRepository
from repository.vergi_usul_kanun_document_repository import VergiUsulKanunDocumentRepository
from repository.ceza_muhakeme_kanun_document_repository import CezaMuhakemeKanunDocumentRepository
from repository.elektronik_ticaretin_duzenlenmesi_kanun_document_repository import ElektronikTicaretinDuzenlenmesiKanunDocumentRepository
from repository.gelir_vergisi_kanun_document_repository import GelirVergisiKanunDocumentRepository
from repository.infaz_kanun_document_repository import InfazKanunDocumentRepository
from repository.kabahatler_kanun_document_repository import KabahatlerKanunDocumentRepository
from repository.kvkk_kanun_document_repository import KvkkKanunDocumentRepository
from repository.medeni_kanun_document_repository import MedeniKanunDocumentRepository
from repository.tuketicinin_korunmasi_kanun_document_repository import TuketicininKorunmasiKanunDocumentRepository
from repository.turk_ticaret_kanun_document_repository import TurkTicaretKanunDocumentRepository
from repository.gumruk_kanun_document_repository import GumrukKanunDocumentRepository
from repository.polis_vazife_salahiyet_kanun_document_repository import PolisVazifeSalahiyetKanunDocumentRepository
from repository.karayollari_trafik_yonetmelik_document_repository import KarayollariTrafikYonetmelikDocumentRepository

from db.model.chat_thread_model import ChatThreadModel
from db.model.pdf_content_model import PdfContentModel
from db.model.message_model import MessageModel
from repository.context_repository import ContextRepository
from util.pdf_selector import PdfSelector
from util.logger import get_logger
from util.prompt_generator import prompt_generator
from agents.web_search_agent import web_search_agent
from agents.pdf_analyzer_agent import pdf_analyzer_agent
from config.config import MESSAGE_HISTORY_SIZE
from config.config import LOOKUP_TABLE


class RagService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._prompt_generator = prompt_generator

        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            self._web_search_agent = web_search_agent
            self._pdf_analyzer_agent = pdf_analyzer_agent
            self._pdf_selector = PdfSelector()
            self._context_repository = ContextRepository()

            # Document repositories injection.
            self._karayollari_trafik_yonetmelik = KarayollariTrafikYonetmelikDocumentRepository(file_path="./pdf/karayollari_trafik_yonetmelik.pdf")
            self._hukuk_muhakemeleri_kanun_repository = HukukMuhakemeleriKanunDocumentRepository(file_path="./pdf/hukuk_muhakemeleri_kanun.pdf") # DEFAULT
            self._icra_ve_iflas_kanun_repository = IcraVeIflasKanunDocumentRepository(file_path="./pdf/icra_ve_iflas_kanun.pdf") # DEFAULT
            self._idari_yargilama_usulu_kanun_repository = IdariYargilamaUsuluKanunDocumentRepository(file_path="./pdf/idari_yargilama_usulu_kanun.pdf") # DEFAULT
            self._turk_anayasasi_repository = TurkAnayasasiDocumentRepository(file_path="./pdf/turk_anayasasi.pdf") # DEFAULT
            self._is_isci_kanun_repository = IsIsciKanunDocumentRepository(file_path="./pdf/is_isci_kanun.pdf")
            self._borclar_kanun_repository = BorclarKanunDocumentRepository(file_path="./pdf/borclar_kanun.pdf")
            self._sinai_mulkiyet_kanun_repository = SinaiMulkiyetKanunDocumentRepository(file_path="./pdf/sinai_mulkiyet_kanun.pdf")
            self._turk_ceza_kanun_repository = TurkCezaKanunDocumentRepository(file_path="./pdf/turk_ceza_kanun.pdf")
            self._rekabetin_korunmasi_kanun_repository = RekabetinKorunmasiKanunDocumentRepository(file_path="./pdf/rekabetin_korunmasi_hakkinda_kanun.pdf")
            self._vergi_usul_kanun_repository = VergiUsulKanunDocumentRepository(file_path="./pdf/vergi_usul_kanun.pdf")
            self._ceza_muhakeme_kanun_repository = CezaMuhakemeKanunDocumentRepository(file_path="./pdf/ceza_muhakeme_kanun.pdf")
            self._elektronik_ticaretin_duzenlenmesi_kanun_repository = ElektronikTicaretinDuzenlenmesiKanunDocumentRepository(file_path="./pdf/elektronik_ticaretin_duzenlenmesi_hakkinda_kanun.pdf")
            self._gelir_vergisi_kanun_repository = GelirVergisiKanunDocumentRepository(file_path="./pdf/gelir_vergisi_kanunu.pdf")
            self._infaz_kanun_repository = InfazKanunDocumentRepository(file_path="./pdf/infaz_kanun.pdf")
            self._kabahatler_kanun_repository = KabahatlerKanunDocumentRepository(file_path="./pdf/kabahatler_kanun.pdf")
            self._kvkk_kanun_repository = KvkkKanunDocumentRepository(file_path="./pdf/kvkk_kanun.pdf")
            self._medeni_kanun_repository = MedeniKanunDocumentRepository(file_path="./pdf/medeni_kanun.pdf")
            self._tuketicinin_korunmasi_kanun_repository = TuketicininKorunmasiKanunDocumentRepository(file_path="./pdf/tuketicinin_korunmasi_hakkinda_kanun.pdf")
            self._turk_ticaret_kanun_repository = TurkTicaretKanunDocumentRepository(file_path="./pdf/turk_ticaret_kanun.pdf")
            self._polis_vazife_salahiyet_kanun_repository = PolisVazifeSalahiyetKanunDocumentRepository(file_path="./pdf/polis_vazife_salahiyet_kanun.pdf")
            self._gumruk_kanun_repository = GumrukKanunDocumentRepository(file_path="./pdf/gumruk_kanun.pdf")




        except Exception as e:
            self._logger.error(f"Error initializing RagService: {e}")

    async def _select_pdfs(
            self,
            query: str
    ) -> list[str]:
        result: list = []
        # Try agent-based selector first, fallback to legacy selector if error/empty
        try:
            result = await self._pdf_selector.aselect_with_agent(query)
            self._logger.info(f"Selected pdfs (agent): {result}")
        except Exception as e:
            self._logger.error(f"PDF selector agent error: {e}")
            result = await self._pdf_selector.aselect({"input": query})
            self._logger.info(f"Selected pdfs (legacy): {result}")

        return result

    async def _retrieve_document_content(
            self,
            query: str,
            conversation_history: list[dict[str, str]]
    ) -> str:
        result: str = ""
        try:
            pdfs: list = await self._select_pdfs(query)
            self._logger.info(f"Selected pdfs: {pdfs}")

            for pdf in pdfs:
                if pdf in LOOKUP_TABLE:
                    retrieval_result = await LOOKUP_TABLE[pdf](self, query, conversation_history)
                    self._logger.info(f"{pdf} result: {retrieval_result}")
                    result += retrieval_result

        except Exception as e:
            self._logger.error(f"Error retrieving rag: {e}")
            traceback.print_exc()

        return result

    async def _retrieve_web_search_content(
            self,
            query: str,
            contents: list
    ) -> list[dict[str, str]]:
        web_search_result: list[dict[str, str]] = []
        try:
            self._logger.info(f"Web search started for query: {query}")
            web_search_result = await self._web_search_agent.search_web(query, contents)
        except Exception as e:
            self._logger.error(f"Error during web search: {e}")
        return web_search_result

    async def _update_chat_thread(
            self,
            chat_thread: ChatThreadModel
    ) -> bool:
        is_updated: bool = False
        chat_thread.updated_at = datetime.datetime.now().isoformat()
        self._logger.info(f"Updating chat thread: {chat_thread.chat_id}")
        update_crud_result = await self._context_repository.update_one(chat_thread)
        if not update_crud_result:
            self._logger.error(f"Failed to update chat thread: {chat_thread.chat_id}")
            is_updated = False
        if update_crud_result:
            self._logger.info(f"Chat thread updated successfully: {chat_thread.chat_id}")
            is_updated = True
        return is_updated

    async def run(
            self,
            query: str,
            chat_thread: ChatThreadModel,
            web_search: bool
    ) -> dict:
        result: dict = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        web_search_results: list[dict[str, str]]
        web_sources: list[str] | None = None
        pdf_content: list[PdfContentModel] = []

        # Fetch contents (context history or message history you can say).
        contents: list = [str({"role": msg.role, "content": msg.content}) for msg in
                          chat_thread.history[-MESSAGE_HISTORY_SIZE:]]

        if len(chat_thread.pdf_content) > 0:
            pdf_content = chat_thread.pdf_content

        # Retrieve information from vector db repositories.
        document_content: str = await self._retrieve_document_content(query, contents)

        # Generate system instructions
        prompt: str = self._prompt_generator.generate_rag_agent_prompt(rag_content=document_content, user_query=query,
                                                                       pdf_content=pdf_content)

        # If web search is asked.
        if web_search:
            web_search_results = await self._retrieve_web_search_content(query, contents)
            contents.extend([str(result) for result in web_search_results])
            web_sources = [result.get("page_url", "") for result in web_search_results if result is not None]

        # Generate content with Gemini.
        try:
            contents.append(prompt)
            response = await self._gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents
            )
        except Exception as e:
            result.update({"code": 200,
                           "success": False,
                           "message": "Sistemde yaşanan bir aksaklık sebebiyle şu an size yardımcı olamıyorum.",
                           "error": str(e),
                           "data": {"response": "Sistemde yaşanan bir aksaklık sebebiyle şu an size yardımcı olamıyorum."}})
            self._logger.error(f"Error generating response: {e}")
            return result

        # Only update chat thread if the gemini response is successful.
        # Create a new message model and update them accordingly.
        chat_thread.history.append(MessageModel(created_at=datetime.datetime.now().isoformat(), role="user",
                                                content=query, web_sources=None))
        chat_thread.history.append(MessageModel(created_at=datetime.datetime.now().isoformat(), role="ai",
                                                content=response.text,
                                                web_sources=web_sources))

        _: bool = await self._context_repository.update_one(chat_thread)
        # Try three more times, then leave it.
        if not _:
            for i in range(3):
                self._logger.error(f"Something went wrong while updating chat thread: {chat_thread.chat_id}")
                is_updated = await self._update_chat_thread(chat_thread)
                if is_updated:
                    result.update({
                        "code": 200,
                        "success": True,
                        "message": "RAG Sorgusu başarıyla tamamlandı.",
                        "data": {"response": response.text}})
                    break
                if i == 2:
                    self._logger.error(f"Failed to update chat thread after 3 attempts: {chat_thread.chat_id}")
                    result.update({"code": 200,
                                   "success": False,
                                   "message": "Sohbet sırasında bir şeyler ters gitti!.",
                                   "data": {"response": "Şu anda size yardımcı olamıyorum."}})
                    return result
        result.update({"code":200, "success": True, "message": "RAG query processed successfully", "data": {"response": response.text}})
        return result

rag_service = RagService()