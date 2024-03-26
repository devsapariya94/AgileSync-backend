from flask import Flask, Blueprint
import os
import dotenv
import flask_cors
# Load the environment variables
dotenv.load_dotenv()

app = Flask(__name__)

# Enabling CORS
flask_cors.CORS(app)


# Importing the blueprint
from app.auth import auth
from app.models import db
from app.views import views
from app.config import Config

# Registering the blueprint
app.register_blueprint(auth)
app.register_blueprint(views)


# Configuring the app
app.config.from_object(Config)


if __name__ == '__main__':
    app.run(debug=True)
