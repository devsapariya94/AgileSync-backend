from flask import Blueprint, request, jsonify
from . import models
from . import views
import jwt


auth = Blueprint('auth', __name__)

from . import views  
from . import models    
from . import config


@auth.route('/login')
def login():
        return 'Login'

@auth.route('/logout')
def logout():
    return 'Logout'

@auth.route('/register', methods=['POST'])
def register():
    request_data = request.get_json()
    username = request_data['username']
    password = request_data['password']
    email = request_data['email']
    try: 
        if models.User.get_user(username):
            return_data = {
                'message': 'User already exists',
                "status": "error"
            }
            return return_data
        else:
            user = models.User(username, password, email)
            user.save()
            return_data = {
                'message': 'User created',
                "status": "success"
            }
            return return_data 

    except:
        return_data = {
            'message': 'An error occurred',
            "status": "error"
        }
        return return_data
    