from flask import Blueprint
from . import models
from . import views
import jwt



auth = Blueprint('auth', __name__)

from . import views  
from . import models    

def verify_token(token):
    try:
        jwt.decode(token, 'secret', algorithms=['HS256'])
        return True
    except:
        return False

@auth.route('/login')
def login():
    return 'Login'

@auth.route('/logout')
def logout():
    return 'Logout'
