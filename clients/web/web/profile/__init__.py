from flask import Blueprint

bp = Blueprint("profile", __name__)

from web_client.profile import routes
