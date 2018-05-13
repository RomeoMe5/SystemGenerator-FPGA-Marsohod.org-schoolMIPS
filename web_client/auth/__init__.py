from flask import Blueprint

bp = Blueprint('auth', __name__)

from web_client.auth import routes
