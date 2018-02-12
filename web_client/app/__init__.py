from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from web_client.app.log import enable_logging_to_file
from configs.web_client import Config

APP = Flask(__name__)
APP.config.from_object(Config)

DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)

LOGIN_M = LoginManager(APP)
LOGIN_M.login_view = "login"

enable_logging_to_file(APP)

from web_client.app import errors, models, routes
