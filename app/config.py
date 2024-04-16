import os
class Config:
    SECRET_KEY = 'your_secret_key'
    DEBUG = True

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
USER_COLLECTION = os.getenv('USER_COLLECTION')
BLACKLIST_TOKEN_COLLECTION = os.getenv('BLACKLIST_TOKEN_COLLECTION')
PROJECT_COLLECTION = os.getenv('PROJECT_COLLECTION')
TASK_COLLECTION = os.getenv('TASK_COLLECTION')
FACULTY_COLLECTION = os.getenv('FACULTY_COLLECTION')
ANNOUNCEMENT_COLLECTION = os.getenv('ANNOUNCEMENT_COLLECTION')
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')