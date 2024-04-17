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
faculty_collection = db[config.FACULTY_COLLECTION]
announcement_collection = db[config.ANNOUNCEMENT_COLLECTION]
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
    def __init__(self, title, description, purpose, owner, mentor, start_date, end_date,duration = "", team = [], objectives = None, documents = None, requirements= [], tasks = []):
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
        self.start_date = start_date
        self.end_date = end_date

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
            'tasks': self.tasks,
            "start_date": self.start_date,
            "end_date": self.end_date
                    
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
    
    def get_project_by_participant(team_member):
        projects = []

        # find all the projects the user is in the list of team member
        for project in project_collection.find({'team': team_member}):
            projects.append(project)

        for project in project_collection.find({'owner': team_member}):
            projects.append(project)

        return projects
    
    def check_if_user_is_owner(project_id, owner):
        project = project_collection.find_one({'project_id': project_id})
        if project['owner'] == owner:
            return True
        return False

    def add_team_member(project_id, team_member):
        a = {'project_id': project_id}
        b = {'$push': {'team': team_member}}
        project_collection.update_one(a,b)

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
    def __init__ (self, title,assignee, project_id, start_date, end_date, status = None, priority = None, subtask = None, tags = None, description = None):
        self.task_id = get_unique_task_id()
        self.title = title
        self.duration = ""
        self.assignee = assignee
        self.status = status
        self.priority = priority
        self.subtask = subtask
        self.tags = tags
        self.description = description
        self.project_id = project_id
        self.start_date = start_date
        self.end_date = end_date
        

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
            'project_id': self.project_id,
            'start_date': self.start_date,
            'end_date': self.end_date
        })

        return self.task_id
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
        print(subtask)

        task_collection.update_one(a,b)

    def update_task_tags(task_id, tags):
        a = {'task_id': task_id}
        b = {'$set': {'tags': tags}}
        task_collection.update_one(a,b)

    def get_task_by_assignee(assignee):
        task = task_collection.find({'assignee': assignee})
        return task
    

class Faculty:
    def __init__(self, name, email, department,password, profile_picture = None):
        self.name = name
        self.email = email
        self.department = department
        self.profile_picture = profile_picture
        self.password = password

    def save(self):
        faculty_collection.insert_one({
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'profile_picture': self.profile_picture,
            'password': self.password
        })

    def get_faculty(email):
        faculty = faculty_collection .find_one({'email': email})
        return faculty

    def update_profile_picture(email, profile_picture):
        a = {'email': email}
        b = {'$set': {'profile_picture': profile_picture}}
        faculty_collection.update_one(a,b)
    
    def get_profile_picture(email):
        faculty = faculty_collection.find_one({'email': email})
        return faculty['profile_picture']
    
    def get_faculty_by_department(department):
        faculty = faculty_collection.find({'department': department})
        return faculty
    

def get_unique_announcement_id():
    announcement_id = random.randint(10000, 9999999 )
    while announcement_collection.find_one({'announcement_id': announcement_id}):
        announcement_id = random.randint(100000, 999999)
    return announcement_id

class Announcement:
    def __init__(self,announcement_id, title, description, owner, team_size, start_date, end_date):
        self.announcement_id = announcement_id
        self.title = title
        self.description = description
        self.owner = owner
        self.team_size = team_size
        self.duration = ""
        self.start_date = start_date
        self.end_date = end_date



    def save(self):
        announcement_collection.insert_one({
            'announcement_id': self.announcement_id,
            'title': self.title,
            'description': self.description,
            'owner': self.owner,
            'team_size': self.team_size,
            'duration' : self.duration,
            'start_date': self.start_date,
            'end_date': self.end_date
        })
            
        return self.announcement_id

    def get_announcement(announcement_id):
        announcement = announcement_collection.find_one({'announcement_id': announcement_id})
        return announcement

    def get_announcement_by_owner(owner):
        announcement = announcement_collection.find({'owner': owner})
        return announcement

