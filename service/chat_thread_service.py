import datetime
import os
import traceback
import sys

from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from meta.singleton import Singleton
from repository.context_repository import ContextRepository
from util.logger import get_logger
from util.uuid_generator import uuid_generator

class ChatThreadService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._context_repository = ContextRepository()

    async def create_chat_thread(
            self,
            chat_name: str
    ) -> ChatThreadModel | None:
        self._logger.info(f"Creating chat thread with name: {chat_name}")
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

    async def retrieve_all_chat_threads(self) -> list[ChatThreadModel] | None:
        self._logger.info("Retrieving all chat threads")
        chat_threads: list[ChatThreadModel] = await self._context_repository.get_all()

        return chat_threads

    async def retrieve_chat_thread(
            self,
            chat_id: str
    ) -> ChatThreadModel | None:
        self._logger.info(f"Retrieving chat thread: {chat_id}")
        result: ChatThreadModel | None = await self._context_repository.get_one_by_id(chat_id)

        return result