from app.core.database.mongodb import MongoDBConnection

class ConsumerRepository:

    def __init__(self):
        self.db = MongoDBConnection().get_database()
        self.consumers = self.db["consumers"]

    def insert_consumer(self,consumer):
        return self.consumers.insert_one(consumer)

    def get_consumer(self,consumer_id):
        return self.consumers.find_one({
            "consumer_id":consumer_id
        })


    