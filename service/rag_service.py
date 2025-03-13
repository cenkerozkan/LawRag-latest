import datetime
import os
import traceback
import sys

from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from meta.singleton import Singleton
from repository.worker_laws_document_repository import WorkerLawsDocumentRepository
from repository.postgresql_document_repository import ObligationsLawsDocumentRepository
from repository.context_repository import ContextRepository
from util.pdf_selector import PdfSelector
from util.logger import get_logger
from util.uuid_generator import uuid_generator
from util.prompt_generator import PromptGenerator

from starlette.concurrency import run_in_threadpool
from google import genai

class RagService(metaclass=Singleton):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._prompt_generator = PromptGenerator()

        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            self._pdf_selector = PdfSelector()
            self._context_repository = ContextRepository()
            self._worker_laws_repository = WorkerLawsDocumentRepository(file_path="./pdf/is_isci_kanun.pdf")
            self._obligations_laws_repository = ObligationsLawsDocumentRepository(file_path="./pdf/borclar_kanun.pdf")
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
            query: str
    ) -> str:
        result: str = ""

        try:
            pdfs = await self._select_pdfs(query)
            self._logger.info(f"Selected pdfs: {pdfs}")
            for pdf in pdfs:
                if pdf == "is_isci_kanun":
                    work_laws_result = self._worker_laws_repository.retrieve(query)
                    self._logger.info(f"Work laws result: {work_laws_result}")
                    result += work_laws_result
                elif pdf == "borclar_kanun":
                    obligations_laws_result = self._obligations_laws_repository.retrieve(query)
                    self._logger.info(f"Obligations laws result result: {obligations_laws_result}")
                    result += obligations_laws_result

        except Exception as e:
            self._logger.error(f"Error retrieving rag: {e}")
            traceback.print_exc(file=sys.stdout)

        return result

    async def _update_chat_thread(
            self,
            chat_thread: ChatThreadModel
    ) -> bool:
        is_updated: bool

        chat_thread.updated_at = datetime.datetime.now().isoformat()
        self._logger.info(f"Updating chat thread: {chat_thread.chat_id}")
        is_updated = await self._context_repository.update_one(chat_thread)

        return is_updated

    async def send_message(
            self,
            query: str,
            chat_thread: ChatThreadModel
    ) -> str:
        message_model: MessageModel = MessageModel(
            created_at=datetime.datetime.now().isoformat(),
            role="user",
            content=query
        )
        chat_thread.history.append(message_model)
        chat_thread.updated_at = datetime.datetime.now().isoformat()

        document_content: str = await self._retrieve_document_content(query)
        self._logger.info(f"DOCUMENT: {document_content}")
        prompt: str = self._prompt_generator.generate_prompt(rag_content=document_content, user_query=query)
        response: any
        try:
            contents: list = [str({"role": msg.role, "content": msg.content}) for msg in chat_thread.history[-25:]]
            contents.append(prompt)
            #self._logger.info(f"Contents: {contents}")
            response = self._gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents
            )

        except Exception as e:
            self._logger.error(f"Error generating response: {e}")
            return "I am unable to generate a response at this time."

        chat_thread.history.append(MessageModel(
            created_at=datetime.datetime.now().isoformat(),
            role="ai",
            content=response.text
        ))
        is_updated: bool = await self._context_repository.update_one(chat_thread)
        return response.text