import datetime
import os
import traceback
import sys

from starlette.concurrency import run_in_threadpool
from google import genai

from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from repository.worker_laws_document_repository import WorkerLawsDocumentRepository
from repository.obligations_laws_document_repository import ObligationsLawsDocumentRepository
from repository.industrial_property_laws_document_repository import IndustrialPropertyLawsDocumentRepository
from repository.turkish_criminal_law_document_repository_document_repository import TurkishCriminalLawDocumentRepository
from repository.context_repository import ContextRepository
from util.pdf_selector import PdfSelector
from util.logger import get_logger
from util.prompt_generator import prompt_generator
from agents.web_search_agent import web_search_agent
from agents.hyde_generator_agent import hyde_generator_agent
from config.config import MESSAGE_HISTORY_SIZE

# This is for making document retrieval much more easy.
# Change the lookup table to use the repository instances
_LOOKUP_TABLE: dict = {
    "is_isci_kanun": lambda self, query: self._worker_laws_repository.aretrieve(query),
    "borclar_kanun": lambda self, query: self._obligations_laws_repository.aretrieve(query),
    "sinai_mulkiyet_kanun": lambda self, query: self._industrial_property_laws_repository.aretrieve(query),
    "turk_ceza_kanun": lambda self, query: self._turkish_criminal_law_repository.aretrieve(query)
}

class RagService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._prompt_generator = prompt_generator

        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            self._web_search_agent = web_search_agent
            self._pdf_selector = PdfSelector()
            self._context_repository = ContextRepository()

            # Document repositories injection.
            self._worker_laws_repository = WorkerLawsDocumentRepository(file_path="./pdf/is_isci_kanun.pdf")
            self._obligations_laws_repository = ObligationsLawsDocumentRepository(file_path="./pdf/borclar_kanun.pdf")
            self._industrial_property_laws_repository = IndustrialPropertyLawsDocumentRepository(file_path="./pdf/sinai_mulkiyet_kanun.pdf")
            self._turkish_criminal_law_repository = TurkishCriminalLawDocumentRepository(file_path="./pdf/turk_ceza_kanun.pdf")

            # Initialize the document repositories.
            #self._worker_laws_repository.init_documents()
            #self._obligations_laws_repository.init_documents()
            #self._industrial_property_laws_repository.init_documents()
            #self._turkish_criminal_law_repository.init_documents()

        except Exception as e:
            self._logger.error(f"Error initializing RagService: {e}")

    async def _select_pdfs(
            self,
            query: str
    ) -> list[str]:
        result: list = []

        result = await self._pdf_selector.aselect({"input": query})
        self._logger.info(f"Selected pdfs: {result}")

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

            # First try with HyDE generated content
            hyde_result = await hyde_generator_agent.generate_hyde_content(
                query=query,
                conversation_history=conversation_history,
                selected_pdfs=pdfs
            )

            # Check if HyDE agent returned the string "false"
            hyde_data = hyde_result["data"]
            if hyde_data == "false":
                search_query = query
                self._logger.info("HyDE agent returned 'false' as data, using original query")
            else:
                search_query = hyde_data if hyde_result["success"] else query
                self._logger.info(f"Using {'HyDE' if hyde_result['success'] else 'original'} query: {search_query}")

            for pdf in pdfs:
                if pdf in _LOOKUP_TABLE:
                    retrieval_result = await _LOOKUP_TABLE[pdf](self, search_query)
                    self._logger.info(f"{pdf} result: {retrieval_result}")
                    result += retrieval_result

        except Exception as e:
            self._logger.error(f"Error retrieving rag: {e}")
            traceback.print_exc(file=sys.stdout)

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
        is_updated: bool

        chat_thread.updated_at = datetime.datetime.now().isoformat()
        self._logger.info(f"Updating chat thread: {chat_thread.chat_id}")
        update_crud_result = await self._context_repository.update_one(chat_thread)
        if not update_crud_result.get("success"):
            self._logger.error(f"Something went wrong while updating chat thread: {chat_thread.chat_id}")
            is_updated = False
        is_updated = True
        return is_updated

    async def run(
            self,
            query: str,
            chat_thread: ChatThreadModel,
            web_search: bool
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": ""
        }
        web_search_results: list[dict[str, str]]
        # Fetch contents (context history or message history you can say).
        contents: list = [str({"role": msg.role, "content": msg.content}) for msg in
                          chat_thread.history[-MESSAGE_HISTORY_SIZE:]]
        # Retrieve information from vector db repositories.
        document_content: str = await self._retrieve_document_content(query, contents)
        # Generate system instructions
        prompt: str = self._prompt_generator.generate_main_prompt(rag_content=document_content, user_query=query)

        # If web search is asked.
        if web_search:
            web_search_results = await self._retrieve_web_search_content(query, contents)
            contents.extend([str(result) for result in web_search_results])

        # Generate content with Gemini.
        try:
            contents.append(prompt)
            response = self._gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents
            )
        except Exception as e:
            result.update({"success": False,
                           "message": "Sistemde yaşanan bir aksaklık sebebiyle şu an size yardımcı olamıyorum.",
                           "error": str(e)})
            self._logger.error(f"Error generating response: {e}")
            return result

        # Only update chat thread if the gemini response is successful.
        # Create a new message model and update them accordingly.
        chat_thread.history.append(MessageModel(created_at=datetime.datetime.now().isoformat(), role="user",
                                                content=query, web_sources=[]))
        chat_thread.history.append(MessageModel(created_at=datetime.datetime.now().isoformat(), role="ai",
                                                content=response.text,
                                                web_sources=[result.get("page_url", "") for result in web_search_results] if web_search else []))

        _: dict = await self._context_repository.update_one(chat_thread)
        # Try three more times, then leave it.
        if not _["success"]:
            for i in range(3):
                self._logger.error(f"Something went wrong while updating chat thread: {chat_thread.chat_id}")
                is_updated = await self._update_chat_thread(chat_thread)
                if is_updated:
                    result.update({
                        "success": True,
                        "message": "RAG query processed successfully",
                        "data": {"response": response.text}})
                    break
        result.update({"code":200, "success": True, "message": "RAG query processed successfully", "data": {"response": response.text}})
        return result

rag_service = RagService()