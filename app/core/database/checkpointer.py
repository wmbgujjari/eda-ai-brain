from pymongo import MongoClient

from langgraph.checkpoint.mongodb import MongoDBSaver

from app.core.config.settings import (
    MONGODB_URI,
    MONGODB_DATABASE
)


client = MongoClient(MONGODB_URI)

checkpointer = MongoDBSaver(
    client,
    db_name=MONGODB_DATABASE
)