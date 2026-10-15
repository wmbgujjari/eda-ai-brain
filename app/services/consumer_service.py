from app.repositories.consumer_repository import ConsumerRepository

class ConsumerService():

    def __init__(self):

        self.repository = ConsumerRepository()


    def get_consumer(self,consumer_id):

        consumer = self.repository.get_consumer(consumer_id)

        if consumer is None:
            return None

        return consumer


    def get_consumption_level(self,consumer_id):

        consumer = self.repository.get_consumer(consumer_id)

        if consumer is None:
            return None
        
        consumption = consumer["monthly_consumption"]

        if consumption < 100:
            level = "LOW"

        elif consumption <=300:
            level = "MEDIUM"
        
        else:
            level = "HIGH"

        return {
            "consumer_id": consumer["consumer_id"],
            "monthly_consumption": consumption,
            "consumption_level": level
        }




