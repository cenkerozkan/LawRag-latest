from pymongo import AsyncMongoClient

from base.mongodb_repository_base import MongoDBRepositoryBase
from db.model.message_model import MessageModel
from util.logger import get_logger
from db.mongodb_connector import MongoDBConnector
from db.model.chat_thread_model import ChatThreadModel

class ContextRepository(MongoDBRepositoryBase):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._db = MongoDBConnector().client["context"]
        self._collection = self._db["chat_history"]

    # Ensure database setup
    async def _ensure_db_setup(self) -> None:
        self._logger.info("Ensuring database setup")
        try:
            # List all databases
            db_list = await self._db.client.list_database_names()

            # Check if our database exists
            if "context" not in db_list:
                self._logger.warn("Creating new database")
                await self._db.command({"create": "chat_history"})
                self._logger.info("Created context database")

            # Check if collection exists
            collections = await self._db.list_collection_names()
            if "chat_history" not in collections:
                await self._db.create_collection("chat_history")
                self._logger.info("Created chat_history collection")

            # Create indexes
            await self._collection.create_index("chat_id", unique=True)
            self._logger.info("Created index on chat_id")

            self._logger.info("Database setup completed successfully")
        except Exception as e:
            self._logger.error(f"Database setup error: {e}")

    async def insert_one(
            self,
            document: ChatThreadModel
    ) -> bool:
        self._logger.info(f"Inserting document: {document}")
        try:
            await self._collection.insert_one(document.model_dump())
            return True
        except Exception as e:
            self._logger.error(e)
            return False

    async def insert_many(
            self,
            documents: list[ChatThreadModel]
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": ""
        }
        self._logger.info(f"Inserting documents: {documents}")
        try:
            await self._collection.insert_many([doc.model_dump() for doc in documents])
            result.update({"success": True, "message": "Chat history inserted successfully"})
        except Exception as e:
            result.update({"success": False, "message": "Chat history insertion failed", "error": str(e)})
            self._logger.error(f"Inserting documents error: {e}")
            raise Exception(e)
        return result

    async def get_one_by_id(
            self,
            id: str
    ) -> ChatThreadModel | None:
        self._logger.info(f"Retrieving document with id: {id}")
        try:
            crud_result = await self._collection.find_one({"chat_id": id})
        except Exception as e:
            self._logger.error(f"Retrieving document error: {e}")
            return None
        if crud_result is None:
            return None
        return ChatThreadModel(**crud_result)

    async def get_one_by_name(
            self,
            name: str
    ) -> ChatThreadModel | None:
        self._logger.info(f"Retrieving document with name: {name}")
        try:
            crud_result = await self._collection.find_one({"chat_name": name})
        except Exception as e:
            self._logger.error(f"Retrieving document error: {e}")
            return None
        if crud_result is None:
            return None
        return ChatThreadModel(**crud_result)

    async def get_all(self):
        raise NotImplementedError

    async def get_all_by_user_id(
            self,
            user_id: str
    ) -> list[ChatThreadModel] | None:
        crud_results: any
        try:
            crud_results = self._collection.find({"user_id": user_id})

        except Exception as e:
            self._logger.error(f"Retrieving documents error: {e}")
            return None
        return [ChatThreadModel(**result) async for result in crud_results]

    async def update_one(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        try:
            await self._collection.update_one(
                {"chat_id": chat_history.chat_id},
                {"$set": chat_history.model_dump()})
            return True
        except Exception as e:
            self._logger.error(f"An error occurred during updating chat.: {e}")
            return False

    async def update_many(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        raise NotImplementedError

    async def delete_one(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        raise NotImplementedError

    async def delete_one_by_id(
            self,
            chat_id: str
    ) -> bool:
        try:
            crud_result: any = await self._collection.delete_one({"chat_id": chat_id})
            if crud_result.deleted_count > 0:
                self._logger.info(f"Chat with id: {chat_id} deleted successfully")
                return True
            else:
                self._logger.warn(f"Chat with id: {chat_id} not found")
                return False
        except Exception as e:
            self._logger.error(f"An error occurred during deletion: {e}")
            return False

    async def delete_many_by_id(
            self,
            ids: list
    ) -> bool:
        try:
            crud_result = await self._collection.delete_many({"chat_id": {"$in": ids}})
            if crud_result.deleted_count > 0:
                self._logger.info(f"Chat with ids: {ids} deleted successfully")
                return True
            else:
                self._logger.warn(f"Chat with ids: {ids} not found")
                return False
        except Exception as e:
            self._logger.error(f"An error occurred during deletion: {e}")
            return False

    async def delete_all_by_user_id(
            self,
            user_id: str
    ) -> bool:
        self._logger.info(f"Deleting all chat histories for user_id: {user_id}")
        try:
            crud_result = await self._collection.delete_many({"user_id": user_id})
            if crud_result.deleted_count > 0:
                return True
            else:
                return False
        except Exception as e:
            self._logger.error(f"An error occurred: {e}")
            return False

    async def get_chat_history(
            self,
            chat_id: str
    ) -> list[MessageModel] | None:
        self._logger.info(f"Retrieving chat history for chat_id: {chat_id}")
        crud_result: any
        try:
            crud_result = await self._collection.find_one({"chat_id": chat_id})
        except Exception as e:
            self._logger.error(f"Retrieving chat history error: {e}")
            return None
        if crud_result:
            return [MessageModel(**message) for message in crud_result.get("history", [])]