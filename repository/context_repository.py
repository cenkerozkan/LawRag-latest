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
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": ""
        }
        self._logger.info(f"Inserting document: {document}")
        try:
            await self._collection.insert_one(document.model_dump())
            result.update({"success": True, "message": "Chat history created successfully"})
        except Exception as e:
            result.update({"success": False, "message": "Chat history creation failed", "error": str(e)})
            self._logger.error(e)
            raise Exception(e)
        return result

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
    ) -> dict[str, str | ChatThreadModel]:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        crud_result: dict = {}
        self._logger.info(f"Retrieving document with id: {id}")
        try:
            crud_result = await self._collection.find_one({"chat_id": id})
        except Exception as e:
            result.update({"success": False, "message": "Sohbet geçmişi getirilirken bir hata oluştu", "error": str(e)})
            self._logger.error(f"Retrieving document error: {e}")
            return result
        if crud_result is None:
            result.update({"success": False, "message": "Böyle bir sohbet geçmişi bulunamadı."})
            return result
        result.update({"success": True, "message": "Sohbet geçmişi başarılı bir şekilde getirildi.",
                       "data": ChatThreadModel(**crud_result)})
        return result

    async def get_one_by_name(
            self,
            name: str
    ) -> dict[str, str | ChatThreadModel]:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        self._logger.info(f"Retrieving document with name: {name}")
        try:
            crud_result = await self._collection.find_one({"chat_name": name})
            result.update({"success": True, "message": "Chat history retrieved successfully", "data": ChatThreadModel(**crud_result)})
        except Exception as e:
            result.update({"success": False, "message": "Chat history retrieval failed", "error": str(e)})
            self._logger.error(f"Retrieving document error: {e}")
        return result

    async def get_all(self) -> dict[str, str | list[ChatThreadModel]]:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        try:
            crud_results = self._collection.find()
            if crud_results is None:
                result.update({"success": False, "message": "No chat history found"})
                return result
            result.update({"success": True, "message": "Chat history retrieved successfully", "data": [ChatThreadModel(**result) async for result in crud_results]})
        except Exception as e:
            result.update({"success": False, "message": "Chat history retrieval failed", "error": str(e)})
            self._logger.error(e)
        return result

    async def get_all_by_user_id(
            self,
            user_id: str
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": []
        }
        try:
            crud_results = self._collection.find({"user_id": user_id})
            if crud_results is None:
                result.update({"success": False, "message": "Herhangi bir sohbet bulunamadı"})
                return result
            result.update({"success": True, "message": "Sohbetler başarıyla getirildi.",
                           "data": [ChatThreadModel(**result).model_dump() async for result in crud_results]})
        except Exception as e:
            result.update({"success": False, "message": "Sohbetlerin getirilmesi esnasında bir hata oluştu",
                           "error": str(e)})
            self._logger.error(e)
        return result

    async def update_one(
            self,
            chat_history: ChatThreadModel
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": ""
        }
        try:
            await self._collection.update_one(
                {"chat_id": chat_history.chat_id},
                {"$set": chat_history.model_dump()})
            result.update({"success": True, "message": "Sohbet başarıyla güncellendi."})
        except Exception as e:
            result.update({"success": False, "message": "Sohbet güncellenirken bir hata meydana geldi",
                           "error": str(e)})
            self._logger.error(f"An error occurred during updating chat.: {e}")
            return result
        return result

    async def update_many(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        raise NotImplementedError

    async def delete_one(
            self,
            chat_history: ChatThreadModel
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": ""
        }
        self._logger.info(f"Deleting document with id: {chat_history.chat_id}")
        try:
            await self._collection.delete_one({"chat_id": chat_history.chat_id})
            result.update({"success": True, "message": "Chat history deleted successfully"})
        except Exception as e:
            result.update({"success": False, "message": "Chat history deletion failed", "error": str(e)})
            self._logger.error(f"An error occured: {e}")
        return result

    async def delete_one_by_id(
            self,
            chat_id: str
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": ""
        }
        try:
            crud_result = await self._collection.delete_one({"chat_id": chat_id})
            if crud_result.deleted_count > 0:
                result.update({"success": True, "message": "Sohbet başarıyla silindi."})
            else:
                result.update({"success": False, "message": "Böyle bir sohbet bulunamadı."})
        except Exception as e:
            result.update({"success": False, "message": "Sohbet silinirken bir hata oluştu.", "error": str(e)})
            self._logger.error(e)

        return result

    async def delete_many_by_id(
            self,
            ids: list
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": ""
        }
        try:
            crud_result = await self._collection.delete_many({"chat_id": {"$in": ids}})
            result.update({"success": True, "message": "Chat history deleted successfully"})
        except Exception as e:
            result.update({"error": str(e)})
            self._logger.error(e)
            raise Exception(e)

        if crud_result.deleted_count > 0:
            result.update({"success": True, "message": "Chat history deleted successfully"})
        else:
            result.update({"success": False, "message": "Something went wrong"})
        return result

    async def delete_all_by_user_id(
            self,
            user_id: str
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": ""
        }
        self._logger.info(f"Deleting all chat histories for user_id: {user_id}")
        try:
            crud_result = await self._collection.delete_many({"user_id": user_id})
            if crud_result.deleted_count > 0:
                result.update({"success": True, "message": "Bütün sohbetler başarılı bir şekilde silindi."})
            else:
                result.update({"success": False, "message": "Bu kullanıcıya bağlı herhangi bir sohbet geçmişi bulunamadı"})
        except Exception as e:
            result.update({"success": False, "message": "Sohbetler silinirken bir hata meydana geldi.",
                           "error": str(e)})
            self._logger.error(f"An error occurred: {e}")
        return result

    async def get_chat_history(
            self,
            chat_id: str
    ) -> dict:
        result: dict = {
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        self._logger.info(f"Retrieving chat history for chat_id: {chat_id}")
        try:
            crud_result = await self._collection.find_one({"chat_id": chat_id})
            if crud_result is None:
                result.update({"success": False, "message": "Sohbet geçmişi bulunamadı."})
                return result
            result.update({"success": True, "message": "Sohbet geçmişi başarıyla getirildi.",
                           "data": {"chat_history": crud_result.get("history")}})
        except Exception as e:
            result.update({"success": False, "message": "Sohbet geçmişi getirilirken bir hata oluştu.",
                           "error": str(e)})
            self._logger.error(e)
        return result