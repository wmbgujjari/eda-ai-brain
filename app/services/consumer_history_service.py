from app.repositories.consumer_history_repository import ConsumerHistoryRepository

class ConsumerHistoryService():

    def __init__(self):

        self.repository = ConsumerHistoryRepository()


    def get_consumer_history(self,consumer_id):

        consumer_history = self.repository.get_consumer_consumption_history(consumer_id)

        if consumer_history is None:
            return None

        return consumer_history

    def get_consumer_history_for_chart(self,consumer_id):

        consumer_history = self.repository.get_consumer_consumption_history(consumer_id)

        chart_data = [];

        for record in consumer_history:
            chart_data.append(
                {
                    "month": f"{record['year']}-{record['month']:02d}",
                    "consumption": record["consumption"]
                }
            )
        return {
            "consumer_id": consumer_id.upper(),
            "chart_type":"line",
            "data":chart_data
        }