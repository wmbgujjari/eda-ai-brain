from app.core.database.mongodb import MongoDBConnection

db_connection = MongoDBConnection()
db = db_connection.get_database()

print("Mongo Database sucessfully Connected")
print("DataBase",db.name)