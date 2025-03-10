import os

from meta.singleton import Singleton

from pymongo import AsyncMongoClient

class MongoDBConnector(metaclass=Singleton):
    def __init__(self):
        self.client: AsyncMongoClient = AsyncMongoClient(os.getenv("MONGO_URI"))