from flask import Flask, Blueprint

app = Flask(__name__)

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
