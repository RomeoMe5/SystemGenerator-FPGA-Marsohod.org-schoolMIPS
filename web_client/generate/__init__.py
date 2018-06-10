from flask import Blueprint

bp = Blueprint('generate', __name__)

from web_client.generate import routes
