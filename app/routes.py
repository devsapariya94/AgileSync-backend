from flask import Blueprint, request, jsonify
from firebase_admin import credentials, storage, initialize_app
import os
import json

routes = Blueprint('routes', __name__)

from . import auth
from . import models

firebase_cred = credentials.Certificate(json.loads(os.getenv('FIREBASE_CREDENTIALS')))
firebase = initialize_app(firebase_cred, {'storageBucket': os.environ['FIREBASE_STORAGE_BUCKET_URL']})

def uploadToFirebase(data, use, filename, project_id=None):
    try:              
        data = data.read()
                
        bucket = storage.bucket(app=firebase)
        
        if use == 'project-documents':
            blob = bucket.blob(f'{use}/{project_id}/{filename}')
            blob.upload_from_string(data, content_type='application/pdf')
        
        elif use == 'profile-pictures':
            blob = bucket.blob(f'{use}/{filename}')
            blob.upload_from_string(data, content_type='image/png')

        blob.make_public()
        return blob.public_url
    
    
    except Exception as e:
        print(e)
        return False
    


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
        public_url= uploadToFirebase(data, 'profile-pictures', filename)

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
    requirements = None
    tasks = None
    
    data = request.get_json()
    title = data['title']
    description = data['description']
    purpose = data['purpose']
    owner = current_user
    mentor = data['mentor']
    duration = data['duration']
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
    
    project_id = models.Project(title, description, purpose, owner, mentor, duration, team, objectives, documents, requirements, tasks).save()

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
@auth.token_required
def add_project_document(current_user):
    project_id = request.form['project_id']
    document = request.files['document']
    filename = document.filename

    project = models.Project.get_project(int(project_id))
    if not project:
        return jsonify({'message': 'Project not found', 'status': 'failed'}), 404
    
    if project['owner'] != current_user and current_user not in project['team']:
        return jsonify({'message': 'You are not allowed to add document to this project', 'status': 'failed'}), 403
    
    filename = f"{project_id}.pdf"

    public_url = uploadToFirebase(document, 'project-documents', filename, project_id)
    
    models.Project.update_project_documents(int(project_id), public_url)
    return jsonify({'message': 'Document added','url':public_url, 'status': 'success'}), 200