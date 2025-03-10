from pymongo import AsyncMongoClient

from base.mongodb_repository_base import MongoDBRepositoryBase
from util.logger import get_logger
from db.mongodb_connector import MongoDBConnector
from db.model.chat_thread_model import ChatThreadModel

class ContextRepository(MongoDBRepositoryBase):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._db = MongoDBConnector().client["context"]
        self._collection = self._db["chat_history"]

    async def insert_one(
            self,
            document: ChatThreadModel
    ) -> bool:
        try:
            await self._collection.insert_one(document.model_dump())

        except Exception as e:
            self._logger.error(e)
            raise Exception(e)
        return True

    async def insert_many(
            self,
            documents: list[ChatThreadModel]
    ) -> bool:
        try:
            await self._collection.insert_many([doc.model_dump() for doc in documents])

        except Exception as e:
            print(e)
            raise Exception(e)
        return True

    async def get_one_by_id(
            self,
            id: str
    ) -> ChatThreadModel | None:
        result: any
        try:
            result = await self._collection.find_one({"chat_id": id})

        except Exception as e:
            self._logger.error(e)
            raise Exception(e)
        return ChatThreadModel(**result) if result else None

    async def get_all(self) -> list[ChatThreadModel] | None:
        results: any
        try:
            results = self._collection.find()

        except Exception as e:
            self._logger.error(e)
            raise Exception(e)

        return [ChatThreadModel(**result) async for result in results]

    async def update_one(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        pass

    async def update_many(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        pass

    async def delete_one_by_id(
            self,
            id: str
    ) -> bool:
        try:
            result = await self._collection.delete_one({"chat_id": id})
        except Exception as e:
            self._logger.error(e)
            raise Exception(e)

        if result.deleted_count == 1:
            return True
        else:
            return False

    async def delete_many_by_id(
            self,
            ids
    ) -> bool:
        try:
            result = await self._collection.delete_many({"chat_id": {"$in": ids}})
        except Exception as e:
            self._logger.error(e)
            raise Exception(e)

        if result.deleted_count > 0:
            return True
        else:
            return False
