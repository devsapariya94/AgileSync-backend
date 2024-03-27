from pymongo import MongoClient
import math
from . import config    

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
users_collection = db[config.USER_COLLECTION]
blacklistToken_collection = db[config.BLACKLIST_TOKEN_COLLECTION]
project_collection = db[config.PROJECT_COLLECTION]
task_collection = db[config.TASK_COLLECTION]


class User:
    def __init__(self, name, password, email):
        self.name = name
        self.password = password
        self.email = email

    def save(self):
        users_collection.insert_one({
            'name': self.name,
            'password': self.password,
            'email': self.email
        })  
      
    def get_user(email):
        user = users_collection.find_one({'email': email})
        return user
    
class BlacklistToken:
   
    def save(token):
        blacklistToken_collection.insert_one({
            'token': token
        })

    def find_one(token):
        return blacklistToken_collection.find_one({'token': token})
    