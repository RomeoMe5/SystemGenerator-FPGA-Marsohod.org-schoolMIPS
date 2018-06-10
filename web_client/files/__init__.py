from flask import Blueprint

bp = Blueprint('files', __name__)

from web_client.files import routes
