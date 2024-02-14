from pymongo import MongoClient

from . import config    

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
users_collection = db[config.USER_COLLECTION]


class User:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def save(self):
        users_collection.insert_one({
            'username': self.username,
            'password': self.password,
            'email': self.email
        })  
      
    def get_user(username):
        user = users_collection.find_one({'username': username})
        return user