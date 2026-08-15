import certifi
from pymongo import MongoClient
from config import MONGO_URL

cliente = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
print(cliente.list_database_names())