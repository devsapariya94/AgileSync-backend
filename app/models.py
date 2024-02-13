from pymongo import MongoClient

from . import config    

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]

