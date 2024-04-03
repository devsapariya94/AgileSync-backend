from flask import Blueprint

views = Blueprint('views', __name__)

from . import auth
from . import models

# hadling the 404 error
@views.app_errorhandler(404)
def page_not_found(e):
    return 'Page not found', 404

 

@views.route('/')
def index():
    return 'Index'
    
@auth.token_required
@views.route('/protected')
def protected(current_user):
    return current_user
    
