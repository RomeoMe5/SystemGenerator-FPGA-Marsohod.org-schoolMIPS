from flask import Blueprint

bp = Blueprint('blog', __name__)

from web_client.blog import routes
