from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads
from configuration import Configuration


app = Flask(__name__)
app.config.from_object(Configuration)

#Data Base
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Login
login = LoginManager(app)
login.login_view = 'login'

#Image uploads
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

from app import routes, models