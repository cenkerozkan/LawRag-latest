from pymongo import AsyncMongoClient

from meta.singleton import Singleton

class ContextRepository(metaclass=Singleton):
    def __init__(self):
        pass

    async def get_all(self):
        pass