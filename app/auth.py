from flask import Blueprint, request, jsonify
import jwt
from functools import wraps
import datetime
from datetime import timedelta
import hashlib

auth = Blueprint('auth', __name__)


from . import models    
from . import config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is invalid'}), 401
      
        if models.BlacklistToken.find_one(token):
            return jsonify({'error': 'Token is invalid'}), 401

        try:
            data = jwt.decode(token, config.Config.SECRET_KEY, algorithms=['HS256'])
            current_user = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token is invalid'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated



def generate_token(user):
    payload = {
        'email': user['email'],  
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, config.Config.SECRET_KEY, algorithm='HS256')
    return token


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
    

@auth.route('/login', methods= ['POST'])
def login():
        request_data = request.get_json()   
        email = request_data['email']
        password = request_data['password']
        password = hash_password(password)

        user = models.User.get_user(email)
        if user:
            if user['password'] == password:
                token = generate_token(user)
                return jsonify({'token': token, 
                                "status" : "success", "role": "user"}), 200
            else:
                return {
                    'message': 'Invalid email or password',
                    'status': 'error'
                }, 406
        
        else:
            faculty = models.Faculty.get_faculty(email)
            if faculty:
                if faculty['password'] == password:
                    token = generate_token(faculty)
                    return jsonify({'token': token, 
                                    "status" : "success", "role":"faculty"}), 200
                else:
                    return {
                        'message': 'Invalid email or password',
                        'status': 'error'
                    }, 406
            else:
                return {
                    'message': 'Invalid email or password',
                    'status': 'error'
                }, 406
            


@auth.route('/logout')
@token_required
def logout(current_user):
    token = request.headers.get('Authorization')
    models.BlacklistToken.save(token)
    return jsonify({'message': 'Successfully logged out'}), 200

@auth.route('/register-faculty', methods=['POST'])
def register_faculty():
    request_data = request.get_json()
    name = request_data['name']
    password = request_data['password']
    password = hash_password(password)
    email = request_data['email']
    department = request_data['department']
    try: 
        if models.Faculty.get_faculty(email):
            return_data = {
                'message': 'Email already exists',
                "status": "error"
            }, 406
            return return_data
        else:
            faculty = models.Faculty(name, email, department, password)

            faculty.save()
            temp_json = {
                'name': name,
                'email': email
            }
            token= generate_token(temp_json)
            return_data = {
                "token": token,
                'message': 'Faculty created',
                "status": "success"
            }, 200
            return return_data 

    except Exception as e:
        print(e)
        return_data = {
            'message': 'An error occurred',
            "status": "error"
        }, 406
        return return_data

@auth.route('/register', methods=['POST'])
def register():
    request_data = request.get_json()
    name = request_data['name']
    password = request_data['password']
    password = hash_password(password)
    email = request_data['email']
    try: 
        if models.User.get_user(email):
            return_data = {
                'message': 'Email already exists',
                "status": "error"
            }, 406
            return return_data
        else:
            user = models.User(name, password, email)

            user.save()
            temp_json = {
                'name': name,
                'email': email
            }
            token= generate_token(temp_json)
            return_data = {
                "token": token,
                'message': 'User created',
                "status": "success"
            }, 200
            return return_data 

    except Exception as e:
        return_data = {
            'message': 'An error occurred',
            "status": "error"
        }, 406
        return return_data
    

