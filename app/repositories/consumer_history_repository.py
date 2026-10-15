from app.core.database.mongodb import MongoDBConnection

class ConsumerHistoryRepository:

    def __init__(self):

        self.db = MongoDBConnection().get_database()
        self.consumer_history = self.db["consumer_history"]
    
    def get_consumer_consumption_history(self,consumer_id):

        consumer_history = list(
            self.consumer_history.find({
                "consumer_id":consumer_id.upper()
            },
            {
                "_id": 0,
                "consumer_id": 1,
                "year": 1,
                "month": 1,
                "consumption": 1
            }
            ).sort(
                [
                    ("year",1),
                    ("month",1)
                ]
            )
        
        )
        return consumer_history