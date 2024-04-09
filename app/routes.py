from flask import Blueprint, request, jsonify
from firebase_admin import credentials, storage, initialize_app
import os
import json

routes = Blueprint('routes', __name__)

from . import auth
from . import models

firebase_cred = credentials.Certificate(json.loads(os.getenv('FIREBASE_CREDENTIALS')))
firebase = initialize_app(firebase_cred, {'storageBucket': os.environ['FIREBASE_STORAGE_BUCKET_URL']})

def uploadToFirebase(data, use, filename):
    try:              
        data = data.read()
                
        bucket = storage.bucket(app=firebase)
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



@routes.route('/addprofile-picture', methods=['POST'])
@auth.token_required
def add_profile_picture(current_user):
        data = request.files['image']
        filename = current_user.replace('@', '_').replace('.', '_').replace('com', '') + '.png'
        public_url= uploadToFirebase(data, 'profile-pictures', filename)

        models.User.update_profile_picture(current_user, public_url)
        return jsonify({'message': f'{public_url}', 'status': 'success'}), 200
    

@routes.route('/getprofile-picture', methods=['GET'])
@auth.token_required
def get_profile_picture(current_user):
    profile_picture = models.User.get_profile_picture(current_user)
    return jsonify({'profile_picture': profile_picture}), 200