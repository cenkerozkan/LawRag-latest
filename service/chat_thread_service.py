import datetime
from fastapi import File, UploadFile
from starlette.concurrency import run_in_threadpool
from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from db.model.pdf_content_model import PdfContentModel
from repository.context_repository import ContextRepository
from util.logger import get_logger
from util.pdf_extractor import extract_text_from_pdf_stream
from util.uuid_generator import uuid_generator
from config.config import EXPECTED_FILE_SIZE
from agents.chat_name_generator_agent import chat_name_generator_agent

class ChatThreadService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._context_repository = ContextRepository()
        self._chat_name_generator_agent = chat_name_generator_agent

    def _is_pdf(
            self,
            file: File(...),
            mime_type: str = "application/pdf"
    ) -> bool:
        if mime_type != file.content_type:
            return False
        return True

    async def create_chat_thread(
            self,
            chat_name: str,
            user_id: str,
            anonymous_user_id: str | None = None
    ) -> dict:
        result = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        self._logger.info(f"Creating chat thread: {chat_name}")
        new_chat: ChatThreadModel = ChatThreadModel(
            chat_name=chat_name,
            chat_id=uuid_generator(),
            user_id=user_id,
            anonymous_user_id=anonymous_user_id,
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            history=[]
        )
        is_inserted: bool = await self._context_repository.insert_one(new_chat)
        if is_inserted:
            result.update({"code": 200, "success": True, "message": "Chat thread created successfully",
                           "data": {"chat": new_chat.model_dump()}})
            return result
        result.update({"code": 500, "success": False, "message": "Chat thread creation failed"})
        self._logger.error(f"Chat thread creation failed")
        return result

    async def delete_chat_thread(
            self,
            chat_id: str
    ) -> dict:
        result = {
            "code": 0,
            "success": False,
            "message": "",
            "data": {},
            "error": ""
        }
        self._logger.info(f"Deleting chat thread: {chat_id}")
        crud_result: bool = await self._context_repository.delete_one_by_id(chat_id)
        if not crud_result:
            self._logger.error(f"Failed to delete chat thread: {chat_id}")
            result.update({"code": 500, "success": False, "message": "Chat thread deletion failed"})
            return result
        result.update({"code": 200, "success": True, "message": "Chat thread deleted successfully"})
        return result

    async def get_all_chat_threads(
            self,
            user_id: str
    ) -> dict:
        result: dict = {
            "code": 0,
            "success": False,
            "message": "",
            "data": {},
            "error": ""
        }
        self._logger.info(f"Getting all chat threads: {user_id}")
        crud_result: list = await self._context_repository.get_all_by_user_id(user_id)
        refined_threads: list
        if crud_result is None:
            self._logger.error(f"Failed to retrieve chat threads")
            result.update({"code": 500, "success": False, "message": "Chat thread retrieval failed"})
            return result
        refined_threads: list = [thread.model_dump(exclude={"history"}) for thread in crud_result]
        result.update({"code": 200, "success": True, "message": "Sohbetler başarıyla alındı",
                       "data": {"threads": refined_threads}})
        return result

    # NOTE: This one is used by RAG service route to fetch the chat data. DO NOT MODIFY OR DELETE IT
    #       IF NOT NEEDED!
    async def retrieve_chat_thread(
            self,
            chat_id: str
    ) -> dict:
        result: dict = {
            "code": 0,
            "success": False,
            "message": "",
            "data": {},
            "error": ""
        }
        self._logger.info(f"Retrieving chat thread: {chat_id}")
        crud_result: ChatThreadModel | None = await self._context_repository.get_one_by_id(chat_id)
        if crud_result is None:
            self._logger.error(f"Failed to retrieve chat thread")
            result.update({"code": 500, "success": False, "message": "Sohbet getirilirken bir sorun oluştu."})
            return result

        result.update({"code": 200, "success": True, "data": crud_result})
        return result

    async def get_chat_history(
            self,
            chat_id: str
    ) -> dict:
        result = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        chat_history: list
        self._logger.info(f"Getting chat history for chat ID: {chat_id}")
        chat_history = await self._context_repository.get_chat_history(chat_id)
        if chat_history is None:
            self._logger.error(f"Failed to retrieve chat history")
            result.update({"code": 500, "success": False, "message": "Chat history retrieval failed"})
            return result
        result.update({"code": 200, "success": True, "message": "Chat history retrieved successfully",
                       "data": {"history": chat_history}})
        return result

    async def delete_all_chat_histories(
            self,
            user_id: str
    ) -> dict:
        result = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        self._logger.info(f"Deleting all chat histories for user: {user_id}")
        crud_result: bool = await self._context_repository.delete_all_by_user_id(user_id)
        if not crud_result:
            self._logger.error(f"Failed to delete chat histories")
            result.update({"code": 500, "success": False, "message": "Chat history deletion failed"})
            return result
        result.update({"code": 200, "success": True, "message": "Chat histories deleted successfully"})
        return result

    async def update_chat_thread_name(
            self,
            chat_id: str,
            chat_name: str
    ) -> dict:
        result: dict = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        self._logger.info(f"Updating chat thread: {chat_id}")
        # First fetch the chat_thread with the given chat_id
        chat_thread: ChatThreadModel = await self._context_repository.get_one_by_id(chat_id)
        if chat_thread is None:
            self._logger.error(f"Failed to retrieve chat thread")
            result.update({"code": 500, "success": False, "message": "Chat thread retrieval failed"})
            return result
        # Update the chat_name
        chat_thread.chat_name = chat_name
        is_updated: bool = await self._context_repository.update_one(chat_thread)
        if not is_updated:
            self._logger.error(f"Failed to update chat thread")
            result.update({"code": 500, "success": False, "message": "Chat thread update failed"})
            return result
        result.update({"code": 200, "success": True, "message": "Chat thread updated successfully",
                       "data": {"chat": chat_thread.model_dump()}})
        return result

    async def generate_chat_name(
            self,
            user_query: str
    ) -> dict:
        result: dict = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        new_chat_name: str = await self._chat_name_generator_agent.generate_chat_name(user_query)
        result.update({"code": 200, "success": True, "message": "Chat thread name generated",
                       "data": {"new_chat_name": new_chat_name}})
        return result

    async def upload_file(
            self,
            file: UploadFile,
            file_name: str,
            chat_id: str
    ) -> dict:
        result: dict = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        if not self._is_pdf(file=file):
            self._logger.error(f"Invalid file type!")
            result.update({"code": 400, "success": False, "message": "Only upload PDF files please"})
            return result

        file_bytes: bytes = await file.read()
        if len(file_bytes) > EXPECTED_FILE_SIZE:
            self._logger.error(f"File too big!")
            result.update({"code": 400, "success": False, "message": "PDF file is too large!"})

        chat_thread: ChatThreadModel = await self._context_repository.get_one_by_id(chat_id)
        if len(chat_thread.pdf_content) == 3:
            self._logger.error(f"Chat thread pdf upload amount exceeded!")
            result.update({"code": 500, "success": False, "message": "Chat thread pdf upload limit exceeded. "
                                                                     "Only 3 pdfs are allowed"})
            return result

        extract_text: dict = await run_in_threadpool(extract_text_from_pdf_stream, file_bytes)

        if not extract_text.get("success"):
            self._logger.error(f"Failed to extract text!")
            result.update({"code": 500, "success": False, "message": "Failed to extract text",
                           "error": extract_text.get("error")})
            return result

        new_pdf_content: PdfContentModel = PdfContentModel(file_name=file_name, file_content=extract_text.get("text"))
        chat_thread.pdf_content.append(new_pdf_content)

        is_updated: bool = await self._context_repository.update_one(chat_thread)
        if not is_updated:
            self._logger.error(f"Failed to update chat thread!")
            result.update({"code": 500, "success": False, "message": "Pdf content update failed"})
            return result
        result.update({"code": 200, "success": True, "message": "Pdf uploaded successfully",})
        return result


chat_thread_service = ChatThreadService()