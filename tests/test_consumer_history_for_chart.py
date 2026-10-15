from app.services.consumer_history_service import ConsumerHistoryService

forchart_service = ConsumerHistoryService()

getchart_data = forchart_service.get_consumer_history_for_chart("C001")

print("\nchart Data")
print(getchart_data)
