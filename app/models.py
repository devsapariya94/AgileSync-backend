from pymongo import MongoClient
import math
from . import config    
import random

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
        self.profile_picture = None
        self.skills = []
    def save(self):
        users_collection.insert_one({
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'skills': self.skills
        })  
      
    def get_user(email):
        user = users_collection.find_one({'email': email})
        return user
    
    def update_profile_picture(email, profile_picture):
        a = {'email': email}
        b = {'$set': {'profile_picture': profile_picture}}
        users_collection.update_one(a,b)
        

    def update_skills(email, skills):
        a = {'email': email}
        b = {'$set': {'skills': skills}}
        users_collection.update_one(a,b)

    def get_profile_picture(email):
        user = users_collection.find_one({'email': email})
        return user['profile_picture']
    
    def get_skills(email):
        user = users_collection.find_one({'email': email})
        return user['skills']
    
        
class BlacklistToken:
   
    def save(token):
        blacklistToken_collection.insert_one({
            'token': token
        })

    def find_one(token):
        return blacklistToken_collection.find_one({'token': token})
    

def get_unique_project_id():
        
        project_id = random.randint(10000, 9999999 )
        while project_collection.find_one({'project_id': project_id}):
            project_id = random.randint(100000, 999999)
        return project_id


class Project:
    def __init__(self, title, description, purpose, owner, mentor, duration, team = [], objectives = None, documents = None, requirements= None, tasks = None):
        self.project_id = get_unique_project_id()
        self.title = title
        self.description = description
        self.purpose = purpose
        self.owner = owner
        self.mentor = mentor
        self.duration = duration
        self.team = team
        self.objectives = objectives
        self.documents = documents
        self.requirements = requirements
        self.tasks = tasks

    def save(self):
        project_collection.insert_one({
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'purpose': self.purpose,
            'owner': self.owner,
            'mentor': self.mentor,
            'duration': self.duration,
            'team': self.team,
            'objectives': self.objectives,
            'documents': self.documents,
            'requirements': self.requirements,
            'tasks': self.tasks
        })
    
        return self.project_id
    
    
    def get_project(project_id):
        project = project_collection.find_one({'project_id': project_id})
        return project
    
    def get_project_documents(project_id):
        project = project_collection.find_one({'project_id': project_id})
        
        if not project:
            return {'message': 'Project not found', 'status': 'failed'}
        
        return project['documents']
        
    def get_project_by_owner(owner):
        # find all projects owned by the user
        project = project_collection.find({'owner': owner})
        return project
    
    def get_project_by_mentor(mentor):
        project = project_collection.find({'mentor': mentor})
        return project
    
    def get_project_by_team_member(team_member):
        project = project_collection.find_one({'team': team_member})
        return project
    
    def add_task(project_id, task):
        a = {'project_id': project_id}
        b = {'$push': {'tasks': task}}
        project_collection.update_one(a,b)

    def get_tasks(project_id):
        project = project_collection.find_one({'project_id': project_id})
        return project['tasks']

    def update_project_documents(project_id, documents):
        a = {'project_id': project_id}
        b = {'$set': {'documents': documents}}
        project_collection.update_one(a,b)
        

def get_unique_task_id(): 
        task_id = random.randint(10000, 9999999 )
        while task_collection.find_one({'task_id': task_id}):
            task_id = random.randint(100000, 999999)
        return task_id
    
    
class Task:
    def __init__ (self, title, duration,assignee, project_id,  status = None, priority = None, subtask = None, tags = None, description = None):
        self.task_id = get_unique_task_id()
        self.title = title
        self.duration = duration
        self.assignee = assignee
        self.status = status
        self.priority = priority
        self.subtask = subtask
        self.tags = tags
        self.description = description
        self.project_id = project_id

    def save(self):
        task_collection.insert_one({
            'task_id': self.task_id,
            'title': self.title,
            'duration': self.duration,
            'assignee': self.assignee,
            'status': self.status,
            'priority': self.priority,
            'subtask': self.subtask,
            'tags': self.tags,
            'description': self.description,
            'project_id': self.project_id
        })

        Project.add_task(self.project_id, self.task_id)

    def get_tasks_by_project(project_id):
        tasks = task_collection.find({'project_id': project_id})
        return tasks
    
    def get_task(task_id):
        task = task_collection.find_one({'task_id': task_id})
        return task

    def update_task_status(task_id, status):
        a = {'task_id': task_id}
        b = {'$set': {'status': status}}
        task_collection.update_one(a,b)

    def update_task_priority(task_id, priority):
        a = {'task_id': task_id}
        b = {'$set': {'priority': priority}}
        task_collection.update_one(a,b)

    def update_task_subtask(task_id, subtask):
        a = {'task_id': task_id}
        b = {'$set': {'subtask': subtask}}
        task_collection.update_one(a,b)

    def update_task_tags(task_id, tags):
        a = {'task_id': task_id}
        b = {'$set': {'tags': tags}}
        task_collection.update_one(a,b)

    def get_task_by_assignee(assignee):
        task = task_collection.find_one({'assignee': assignee})
        return task
    
