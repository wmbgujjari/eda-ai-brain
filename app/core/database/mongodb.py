from pymongo import MongoClient

from app.core.config.settings import (
    MONGODB_DATABASE,MONGODB_URI
)

class MongoDBConnection:

    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.database = self.client[MONGODB_DATABASE]

    def get_database(self):
        return self.database    