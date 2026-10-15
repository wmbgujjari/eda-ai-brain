from app.repositories.consumer_repository import ConsumerRepository

repository = ConsumerRepository()

consumer = {
    "consumer_id" : "C001",
    "name" : "Test Consumer",
    "category" : "Domestic",
    "monthly_consumption" : 250
}

result = repository.insert_consumer(consumer)

print("Insertion Id: ",result.inserted_id)

found_consumer = repository.get_consumer("C001")

print("Retrive Consumer: ",found_consumer)