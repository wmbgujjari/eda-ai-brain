from app.services.consumer_history_service import (
    ConsumerHistoryService
)


repository = ConsumerHistoryService()

records = repository.get_consumer_history("C001")

print("Number of records:", len(records))

for record in records:
    print(record)