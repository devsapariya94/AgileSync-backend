import os
class Config:
    SECRET_KEY = 'your_secret_key'
    DEBUG = True

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
USER_COLLECTION = os.getenv('USER_COLLECTION')
BLACKLIST_TOKEN_COLLECTION = os.getenv('BLACKLIST_TOKEN_COLLECTION')