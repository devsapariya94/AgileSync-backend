from flask import Flask, Blueprint
import os
import dotenv
import flask_cors
# Load the environment variables
dotenv.load_dotenv()

app = Flask(__name__)

# Enabling CORS
flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})


# Importing the blueprint
from app.auth import auth
from app.models import db
from app.routes import routes
from app.config import Config

# Registering the blueprint
app.register_blueprint(auth)
app.register_blueprint(routes)


# Configuring the app
app.config.from_object(Config)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
