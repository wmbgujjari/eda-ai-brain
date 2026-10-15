from langchain.tools import tool
from app.services.consumer_history_service import ConsumerHistoryService

consumer_history_service = ConsumerHistoryService()

@tool
def get_consumer_history(consumer_id: str):

    """ Get the Consumption history of a consumer """
    return consumer_history_service.get_consumer_history(consumer_id)

@tool
def get_consumer_history_for_chart(consumer_id: str):

    """ Get chart data for a consumer's. """
    return consumer_history_service.get_consumer_history_for_chart(consumer_id)    