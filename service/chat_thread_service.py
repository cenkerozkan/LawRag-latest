import datetime
from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from repository.context_repository import ContextRepository
from util.logger import get_logger
from util.uuid_generator import uuid_generator

class ChatThreadService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._context_repository = ContextRepository()

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
        new_chat = ChatThreadModel(
            chat_name=chat_name,
            chat_id=uuid_generator(),
            user_id=user_id,
            anonymous_user_id=anonymous_user_id,
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            history=[]
        )
        crud_result: dict = await self._context_repository.insert_one(new_chat)
        if not crud_result.get("success"):
            self._logger.error(f"Failed to create chat thread")
            result.update({"code": 500, "success": False, "message": crud_result.get("message", ""), "error": crud_result.get("error", "")})
            return result
        result.update({"code": 200, "success": True, "message": "Chat thread created successfully","data": {"chat": new_chat.model_dump()}})
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
        crud_result: dict = await self._context_repository.delete_one_by_id(chat_id)
        if not crud_result.get("success"):
            self._logger.error(f"Failed to delete chat thread")
            result.update({"code": 404, "success": False, "message": crud_result.get("message", ""),
                           "error": crud_result.get("error", "")})
            return result
        result.update({"code": 200, "success": True, "message": crud_result.get("message")})
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
        crud_result: dict = await self._context_repository.get_all_by_user_id(user_id)
        if not crud_result.get("success"):
            self._logger.error(f"Failed to get all chat threads for user: {user_id}")
            result.update({"code": 404, "success": False, "message": crud_result.get("message", ""),
                           "error": crud_result.get("error", "")})
            return result
        if len(crud_result.get("data")) == 0:
            result.update({"code": 200, "success": True, "message": "Herhangi bir sohbet geçmişi bulunamadı."})
            return result
        result.update({"code": 200, "success": True, "message": crud_result.get("message"),
                       "data": {"threads": crud_result.get("data")}})
        return result

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
        crud_result: dict = await self._context_repository.get_one_by_id(chat_id)
        if not crud_result.get("success"):
            result.update({"code": 500, "success": False, "message": crud_result.get("message", ""),
                           "error": crud_result.get("error", "")})
            return result
        if not crud_result.get("data"):
            result.update({"code": 404, "success": False, "message": crud_result.get("message")})
            return result
        result.update({"success": True, "message": "Chat thread retrieved successfully",
                       "data": crud_result.get("data")})
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
        self._logger.info(f"Retrieving chat history for chat: {chat_id}")
        crud_result: dict = await self._context_repository.get_chat_history(chat_id)
        if not crud_result.get("success"):
            self._logger.error(f"Some error occured while retrieving chat history: {crud_result.get('error')}")
            result.update({"code": 500, "success": False, "message": crud_result.get("message", ""),
                           "error": crud_result.get("error", "")})
            return result
        if crud_result.get("data").get("history") is None:
            result.update({"code": 200, "success": crud_result.get("success"), "message": crud_result.get("message"),
                           "data": {"history": crud_result.get("history")}})
            return result
        result.update({"code": 200, "success": True, "message": crud_result.get("message"),
                       "data": {"history": crud_result.get("data")}})
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
        crud_result: dict = await self._context_repository.delete_all_by_user_id(user_id)
        if not crud_result.get("success"):
            self._logger.error(f"Failed to delete all chat histories")
            result.update({"code": 400, "success": False, "message": crud_result.get("message", ""),
                           "error": crud_result.get("error", "")})
            return result
        result.update({"code": 200, "success": True, "message": crud_result.get("message")})
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
        retrieve_chat_result: dict = await self._context_repository.get_one_by_id(chat_id)
        if not retrieve_chat_result.get("success"):
            self._logger.error(f"Failed to retrieve chat thread for update")
            result.update({"code": 404, "success": False, "message": retrieve_chat_result.get("message", ""),
                           "error": retrieve_chat_result.get("error", "")})
            return result
        if retrieve_chat_result.get("data") is None:
            result.update({"code": 404, "success": False, "message": retrieve_chat_result.get("message")})
            return result

        # Retrieve the existing chat thread and create a pydantic model.
        existing_chat_thread: ChatThreadModel = retrieve_chat_result.get("data")
        existing_chat_thread.chat_name = chat_name
        existing_chat_thread.updated_at = datetime.datetime.now().isoformat()
        update_crud_result: dict = await self._context_repository.update_one(existing_chat_thread)
        if not update_crud_result.get("success"):
            self._logger.error(f"Failed to update chat thread")
            result.update({"code": 500, "success": False, "message": update_crud_result.get("message", ""),
                           "error": update_crud_result.get("error", "")})
            return result
        result.update({"code": 200, "success": True, "message": update_crud_result.get("message"),
                       "data": {"chat": existing_chat_thread.model_dump()}})
        return result


chat_thread_service = ChatThreadService()