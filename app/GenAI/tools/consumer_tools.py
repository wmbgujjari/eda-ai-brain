from langchain.tools import tool
from app.services.consumer_service import ConsumerService

consumer_service = ConsumerService()

@tool
def get_consumption_level(consumer_id: str):

    """ Get the Monthly Consumption of a consumer """
    return consumer_service.get_consumption_level(consumer_id)

@tool
def get_consumer(consumer_id: str):

    """ Get the Consumer Details of a Consumer """
    return consumer_service.get_consumer(consumer_id)