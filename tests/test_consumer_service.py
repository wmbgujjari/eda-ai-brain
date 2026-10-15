from app.services.consumer_service import ConsumerService

service = ConsumerService()

consumer = service.get_consumption_level("C001")

print("Consumer Details")
print(consumer)

