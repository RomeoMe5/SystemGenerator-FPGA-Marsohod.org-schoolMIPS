from datetime import datetime
from typing import NoReturn

from flask import current_app, render_template
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries

from fpga_marsohod_generator_engine.boards import BOARDS
from web_client import db
from web_client.main import bp


@bp.before_request
def before_request() -> NoReturn:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.after_app_request
def after_request(response: object) -> NoReturn:
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                "Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s",
                query.statement,
                query.parameters,
                query.duration,
                query.context
            )
    return response


@bp.route('/')
def index() -> object:
    return render_template(
        "index.html",
        title=current_app.config['APP_HEADER'],
        boards=BOARDS
    )
