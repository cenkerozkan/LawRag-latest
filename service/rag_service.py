import datetime
import os
import traceback
import sys

from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from meta.singleton import Singleton
from repository.mongodb_document_repository import MongoDbDocumentRepository
from repository.postgresql_document_repository import PostgreSQLDocumentRepository
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
            self._mongodb_repository = MongoDbDocumentRepository(file_path="./pdf/MongoDB_Cheat_Sheet.pdf")
            self._postgresql_repository = PostgreSQLDocumentRepository(file_path="./pdf/PostgreSQL_Cheat_Sheet.pdf")
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
                if pdf == "mongodb":
                    mongo_result = self._mongodb_repository.retrieve(query)
                    self._logger.info(f"MongoDB result: {mongo_result}")
                    result += mongo_result
                elif pdf == "postgresql":
                    postgres_result = self._postgresql_repository.retrieve(query)
                    self._logger.info(f"PostgreSQL result: {postgres_result}")
                    result += postgres_result

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

    async def retrieve_chat_thread(
            self,
            chat_id: str
    ) -> ChatThreadModel | None:
        self._logger.info(f"Retrieving chat thread: {chat_id}")
        result: ChatThreadModel | None = await self._context_repository.get_one_by_id(chat_id)

        return result

    async def create_new_chat_thread(
            self,
            chat_name: str
    ) -> ChatThreadModel | None:
        new_chat = ChatThreadModel(
            chat_name=chat_name,
            chat_id=uuid_generator(),
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            history=[]
        )

        is_created: bool = await self._context_repository.insert_one(new_chat)
        if is_created:
            return new_chat

        return None

    async def delete_chat_thread(
            self,
            chat_id: str
    ) -> bool:
        self._logger.info(f"Deleting chat thread: {chat_id}")
        is_deleted: bool = await self._context_repository.delete_one_by_id(chat_id)

        return is_deleted

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
            self._logger.info(f"Contents: {contents}")
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