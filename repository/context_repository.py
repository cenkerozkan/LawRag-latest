from pymongo import AsyncMongoClient

from meta.singleton import Singleton
from util.logger import get_logger
from db.mongodb_connector import MongoDBConnector
from db.model.chat_history_model import ChatHistoryModel

class ContextRepository(metaclass=Singleton):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._db = MongoDBConnector().client["context"]
        self._collection = self._db["chat_history"]

    async def insert_one(
            self,
            document: ChatHistoryModel
    ) -> bool:
        try:
            await self._collection.insert_one(document.model_dump())
            return True
        except Exception as e:
            self._logger.error(e)
            return False

    async def insert_many(
            self,
            documents: list[ChatHistoryModel]
    ) -> bool:
        try:
            await self._collection.insert_many([doc.model_dump() for doc in documents])
            return True
        except Exception as e:
            print(e)
            return False

    async def update_one(
            self,
            chat_history: ChatHistoryModel
    ) -> bool:
        pass

    async def update_many(
            self,
            chat_history: ChatHistoryModel
    ) -> bool:
        pass

    async def get_all(self) -> ChatHistoryModel | None:
        pass

    async def get_all_by_id(
            self,
            id: str
    ) -> ChatHistoryModel | None:
        pass