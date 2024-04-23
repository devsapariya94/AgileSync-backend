from flask import Blueprint, request, jsonify
# from firebase_admin import credentials, storage, initialize_app
import os
import json
import requests
import google.generativeai as genai

from appwrite.client import Client
from appwrite.input_file import InputFile
from appwrite.services.storage import Storage
from appwrite.id import ID

routes = Blueprint('routes', __name__)

from . import auth
from . import models

# firebase_cred = credentials.Certificate(json.loads(os.getenv('FIREBASE_CREDENTIALS')))
# firebase = initialize_app(firebase_cred, {'storageBucket': os.environ['FIREBASE_STORAGE_BUCKET_URL']})



def uploadToAppwrite(data, use, filename, project_id=None):

    client = Client()

    (client
    .set_endpoint(os.getenv("APPWRITE_ENDPOINT")) # Your API Endpoint
    .set_project(os.getenv("APPWRITE_PROJECT_ID")) # Your project ID
    .set_key(os.getenv("APPWRTIE_API_KEY")) # Your secret API key
    )

    if use == 'profile-pictures':
        storage = Storage(client)

        try:
            # delete the file if it exists
            storage.delete_file(os.getenv("APPWRITE_BUCKET_ID"), filename)
        except:
            pass

        data = data.read()
        id = filename
        storage.create_file(os.getenv("APPWRITE_BUCKET_ID"), id , InputFile.from_bytes(data, filename=filename))
        bucket = os.getenv("APPWRITE_BUCKET_ID")
        appwrite_project_id = os.getenv("APPWRITE_PROJECT_ID")
        file_url = f"https://cloud.appwrite.io/v1/storage/buckets/{bucket}/files/{id}/view?project={appwrite_project_id}"

        return file_url

    elif use == 'project-documents':
        storage = Storage(client)
        try:
            # delete the file if it exists
            storage.delete_file(os.getenv("APPWRITE_BUCKET_ID"), filename)
        except:
            pass

        data = data.read()
        id = filename
        storage.create_file(os.getenv("APPWRITE_BUCKET_ID"), id , InputFile.from_bytes(data, filename=filename))
        bucket = os.getenv("APPWRITE_BUCKET_ID")
        appwrite_project_id = os.getenv("APPWRITE_PROJECT_ID")
        file_url = f"https://cloud.appwrite.io/v1/storage/buckets/{bucket}/files/{id}/view?project={appwrite_project_id}"

        return file_url



# def uploadToFirebase(data, use, filename, project_id=None):
#     try:              
#         data = data.read()
        
#         bucket = storage.bucket(app=firebase)
#         if use == 'project-documents':
            

#             blob = bucket.blob(f'{use}/{project_id}/{filename}')

#             blob.upload_from_string(data, content_type='application/pdf')
        
#         elif use == 'profile-pictures':
#             blob = bucket.blob(f'{use}/{filename}')
#             blob.upload_from_string(data, content_type='image/png')


#         # create token for the file
#         blob.make_public()
        
#         # refresh the public url in chache to get the updated url 
#         blob.reload()
#         public_url = blob.public_url
#         abc = blob.generate_signed_url(1712983991)
#         return abc
    
    
    
#     except Exception as e:
#         print(e)
#         return False
    


# hadling the 404 error
@routes.app_errorhandler(404)
def page_not_found(e):
    return 'Page not found', 404

 

@routes.route('/')
def index():
    return 'Index'
    

@routes.route('/protected')
@auth.token_required
def protected(current_user):
    respoce_data=  {"email": current_user}

    return respoce_data, 200



@routes.route('/update-profile-picture', methods=['POST'])
@auth.token_required
def add_profile_picture(current_user):
        data = request.files['image']
        filename = current_user.replace('@', '_').replace('.', '_').replace('com', '') + '.png'
        public_url= uploadToAppwrite(data, 'profile-pictures', filename)

        models.User.update_profile_picture(current_user, public_url)
        return jsonify({'message': f'{public_url}', 'status': 'success'}), 200
    

@routes.route('/get-profile-picture', methods=['GET'])
def get_profile_picture():
    email = request.get_json()['email']
    profile_picture = models.User.get_profile_picture(email)
    return jsonify({'profile_picture': profile_picture}), 200


@routes.route('/update-skills', methods=['POST'])
@auth.token_required
def add_skills(current_user):
    skills = request.json['skills']
    models.User.update_skills(current_user, skills)
    return jsonify({'message': 'skills added', 'status': 'success'}), 200

@routes.route('/get-skills', methods=['GET'])
def get_skills():
    email = request.get_json()['email']
    skills = models.User.get_skills(email)
    return jsonify({'skills': skills}), 200

@routes.route('/all-userdata', methods=['GET'])
@auth.token_required
def all_user_data(current_user):
    user = models.User.get_user(current_user)
    data = {
        'name': user['name'],
        'email': user['email'],
        'profile_picture': user['profile_picture'],
        'skills': user['skills']
    }
    return jsonify(data), 200

@routes.route('/create-project', methods=['POST'])
@auth.token_required
def create_project(current_user):
    team = []
    objectives = None
    documents = None
    requirements = []
    tasks = []
    
    data = request.get_json()
    title = data['title']
    description = data['description']
    start_date = data['start_date']
    end_date = data['end_date']
    purpose = data['purpose']
    owner = current_user
    mentor = data['mentor']
    # duration = data['duration']
    if 'team' in data:
        team = data['team']
    elif 'objectives' in data:
        objectives = data['objectives']
    elif 'documents' in data:
        documents = data['documents']
    elif 'requirements' in data:
        requirements = data['requirements']
    elif 'tasks' in data:
        tasks = data['tasks']
    
    project_id = models.Project(
        title=title, description=description, start_date=start_date, end_date=end_date, purpose=purpose, owner=owner, mentor=mentor, team=team, objectives=objectives, documents=documents, requirements=requirements, tasks=tasks).save(
    )
    return jsonify({'message': 'Project created', 
                    'project_id': project_id, 'status': 'success'}), 200

@routes.route('/get-project', methods=['GET'])
@auth.token_required
def get_project(current_user):
    project_id = request.get_json()['project_id']
    project = models.Project.get_project(int(project_id))

    # check if user is the owner or in the team
    if project['owner'] != current_user and current_user not in project['team']:
        return jsonify({'message': 'You are not allowed to view this project', 'status': 'failed'}), 403

    # convert the project id to string
    project["_id"] = str(project["_id"])
    return jsonify(project), 200

@routes.route('/get-project-documents', methods=['GET'])
def get_project_documents():
    project_id = request.get_json()['project_id']
    documents = models.Project.get_project_documents(int(project_id))
    
    try: 
        if documents['status'] == 'failed':
            return jsonify(documents), 404
    except:
        pass
    if not documents:
        return jsonify({'message': 'No document found', 'status': 'success'}), 200
    print(documents)
    return jsonify(documents), 200


@routes.route('/get-project-by-owner', methods=['GET'])
@auth.token_required
def get_project_by_owner(current_user):
    owner = current_user
    print(owner)
    projects = models.Project.get_project_by_owner(owner)
    
    # projects is in mongoDB cursor object so we need to convert it to list
    projects = list(projects)

    # modify the project _id to string
    for project in projects:
        project["_id"] = str(project["_id"])


    return jsonify(projects), 200



@routes.route('/get-project-by-mentor', methods=['GET'])
def get_project_by_mentor():
    mentor = request.get_json()['mentor']
    projects = models.Project.get_project_by_mentor(mentor)

    projects = list(projects)

    for project in projects:
        project["_id"] = str(project["_id"])

    return jsonify(projects), 200


@routes.route('/add-project-document', methods=['POST'])
# @auth.token_required
def add_project_document():
    project_id = request.form['project_id']
    document = request.files['document']
    filename = document.filename

    project = models.Project.get_project(int(project_id))
    if not project:
        return jsonify({'message': 'Project not found', 'status': 'failed'}), 404
    
    # if project['owner'] != current_user and current_user not in project['team']:
    #     return jsonify({'message': 'You are not allowed to add document to this project', 'status': 'failed'}), 403
    
    filename = f"{project_id}_pdf"

    public_url = uploadToAppwrite(document, 'project-documents', filename, project_id)
    print(public_url)
    models.Project.update_project_documents(int(project_id), public_url)
    return jsonify({'message': 'Document added','url':public_url, 'status': 'success'}), 200


@routes.route('/helper-1-for-upload-document', methods=['POST'])
def helper_1_for_upload_document():
    project_id = request.json['project_id']
    project = models.Project.get_project(int(project_id))
    if not project:
        return jsonify({'message': 'Project not found', 'status': 'failed'}), 404
    
    else:
        return jsonify({'message': 'Project found', 'status': 'success'}), 200


@routes.route('/helper-2-for-upload-document', methods=['POST'])
def helper_2_for_upload_document():
    project_id = request.json['project_id']
    public_url = request.files['public_url']
    models.Project.update_project_documents(int(project_id), public_url)
    return jsonify({'message': 'Document added','url':public_url, 'status': 'success'}), 200

@routes.route('/add-team-member', methods=['POST'])
@auth.token_required
def add_team_member(current_user):
    project_id = request.json['project_id']
    team_members = request.json['team_member']

    # check if the user is the owner of the project
    if not models.Project.check_if_user_is_owner(int(project_id), current_user):
        return jsonify({'message': 'You are not allowed to add team members to this project', 'status': 'failed'}), 403
    
    for team_member in team_members:
        models.Project.add_team_member(int(project_id), team_member)
    return jsonify({'message': 'Team members added', 'status': 'success'}), 200

@routes.route('/get-project-by-participant', methods=['GET'])
@auth.token_required
def get_project_by_participant(current_user):
    team_member = current_user
    project = models.Project.get_project_by_participant(team_member)
    print(project)

    # convert the project id to string
    for p in project:
        p["_id"] = str(p["_id"])
        
    return jsonify(project), 200


@routes.route('/add-task', methods=['POST'])
@auth.token_required
def add_task(current_user):
    project_id = request.json['project_id']
    title = request.json['title']
    # duration = request.json['duration']
    start_date = request.json['start_date']
    end_date = request.json['end_date']
    assignee = request.json['assignee']

    description = None
    status = None
    priority = None
    subtask = []
    tags = []

    if 'description' in request.json:
        description = request.json['description']
    if 'status' in request.json:
        status = request.json['status']
    if 'priority' in request.json:
        priority = request.json['priority']
    if 'subtask' in request.json:
        subtask = request.json['subtask']
    if 'tags' in request.json:
        tags = request.json['tags']

    
    task_id = models.Task(
                title=title, description=description, start_date=start_date, end_date=end_date, assignee=assignee, status=status, priority=priority, subtask=subtask, tags=tags, project_id=project_id).save(
    )

    models.Project.add_task(int(project_id), task_id)

    return jsonify({'message': 'Task added', 'task_id': task_id, 'status': 'success'}), 200

@routes.route('/get-all-tasks-by-project', methods=['POST'])
def get_tasks():
    project_id = request.get_json()['project_id']
    tasks = models.Project.get_tasks(int(project_id))
    task_list = []
    for task in tasks:
        task_list.append(models.Task.get_task(task))
    for task in task_list:
        task["_id"] = str(task["_id"])

    return jsonify(task_list), 200

@routes.route('/get-task', methods=['GET'])
def get_all_tasks_by_project():
    task_id = request.get_json()['task_id']
    task = models.Task.get_task(int(task_id))
    task["_id"] = str(task["_id"])                    
    return jsonify(task), 200

@routes.route('/update-task-status', methods=['POST'])
def update_task_status():
    task_id = request.json['task_id']
    status = request.json['status']

    models.Task.update_task_status(int(task_id), status)
    return jsonify({'message': 'Task status updated', 'status': 'success'}), 200

@routes.route('/update-task-priority', methods=['POST'])
def update_task_priority():
    task_id = request.json['task_id']
    priority = request.json['priority']

    models.Task.update_task_priority(int(task_id), priority)
    return jsonify({'message': 'Task priority updated', 'status': 'success'}), 200

@routes.route('/update-task-subtask', methods=['POST'])
def update_task_subtask():
    task_id = request.json['task_id']
    subtask = request.json['subtask']
    print(subtask)
    models.Task.update_task_subtask(int(task_id), subtask)
    return jsonify({'message': 'Task subtask updated', 'status': 'success'}), 200


@routes.route('/update-task-tags', methods=['POST'])
def update_task_tags():
    task_id = request.json['task_id']
    tags = request.json['tags']

    models.Task.update_task_tags(int(task_id), tags)
    return jsonify({'message': 'Task tags updated', 'status': 'success'}), 200


@routes.route('/get-task-by-assignee', methods=['POST'])
def get_task_by_assignee():
    assignee = request.get_json()['assignee']
    tasks = models.Task.get_task_by_assignee(assignee)

    tasks = list(tasks)
    for task in tasks:
        task["_id"] = str(task["_id"])

    return jsonify(tasks), 200


@routes.route('/make-an-announcement', methods=['POST'])
@auth.token_required
def make_an_announcement(current_user):
    if not models.Faculty.get_faculty(current_user):
        return jsonify({'message': 'You are not allowed to make an announcement', 'status': 'failed'}), 403
    
    title = request.json['title']
    description = request.json['description']
    owner = current_user
    team_size = request.json['team_size']
    # duration = request.json['duration']
    start_date = request.json['start_date']
    end_date = request.json['end_date']
    announcement_id = models.get_unique_announcement_id()
    
    models.Announcement(announcement_id= announcement_id, title=title, description=description, owner=owner, team_size=team_size, start_date=start_date, end_date=end_date).save() 
    return jsonify({'message': 'Announcement made', 'status': 'success', "url": f"https://agilesync.co/create-project/{announcement_id}"}), 200


@routes.route('/get-announcement', methods=['GET'])
def get_announcement():
    announcement_id = request.get_json()['announcement_id']
    
    announcement = models.Announcement.get_announcement(int(announcement_id))
    if not announcement:
        return jsonify({'message': 'Announcement not found', 'status': 'failed'}), 404
    mentor = announcement['owner']
    team_size = announcement['team_size']
    duration = announcement['duration']

    return jsonify({'mentor': mentor, 'team_size': team_size, 'duration': duration}), 200


@routes.route('/generate-subtask', methods=['POST'])
def generate_subtask():
    task_id = request.json['task_id']
    project_id = request.json['project_id']

    task = models.Task.get_task(int(task_id))
    project = models.Project.get_project(int(project_id))

    if not task or not project:
        return jsonify({'message': 'Task or project not found', 'status': 'failed'}), 404
    
    from . import config
    exmple = "If the task is create the home page of the website, the subtask could be: ['create the header', 'create the footer', 'add the logo']"

    formate = "['subtask1', 'subtask2', 'subtask3']"
    propt = f"Generate the Subtask for the following task: {task} which is in the following project: {project}. Stricly give the subtask in formate like this: "+formate +"for example: "+exmple + "don't give the unnecessary information. only give the list of subtask in the formate mentioned above."

    genai.configure(api_key=config.GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(propt)
    response_text = response.text.replace("\n","").replace("\r","").replace("\t","")
    return jsonify({'subtasks': response_text}), 200

@routes.route('/get-all-announcements', methods=['GET'])
@auth.token_required
def get_all_announcements(current_user):
    announcements = models.Announcement.get_announcement_by_owner(current_user)

    announcements = list(announcements)
    for announcement in announcements:
        announcement["_id"] = str(announcement["_id"])


    return jsonify(announcements), 200



@routes.route('/get-all-faculty')
def get_all_faculty():
    faculty = models.Faculty.get_all_faculty()
    faculty = list(faculty)
    for f in faculty:
        f["_id"] = str(f["_id"])

    return jsonify(faculty), 200

@routes.route('/get-all-users')
def get_all_users():
    users = models.User.get_all_users()
    users = list(users)
    for user in users:
        user["_id"] = str(user["_id"])

    return jsonify(users), 200
