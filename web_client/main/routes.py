from datetime import datetime

from flask import current_app, render_template
from flask_login import current_user

from engine.boards import BOARDS
from web_client import db
from web_client.main import bp


@bp.before_request
def before_request() -> None:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
def index() -> object:
    return render_template(
        "index.html",
        title=current_app.config['APP_HEADER'],
        boards=BOARDS
    )
