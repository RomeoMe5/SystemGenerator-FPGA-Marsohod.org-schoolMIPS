# [future] TODO delete unused data (optimize memory usage)

import os

from flask import Flask, current_app, request
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify

from configs.web_client import APP_NAME, configs
from web_client.utils.log import (enable_email_error_notifications,
                                  enable_logging_to_file,
                                  enable_logging_to_stdout)


babel = Babel()
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
moment = Moment()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = _l("Please log in to access this page")


class PATHS(object):
    BASE = os.path.dirname(__file__)
    STATIC = os.path.join(BASE, "static")
    FILES = os.path.join(STATIC, "files")  # [dev] TODO change folder
    TRANSL = os.path.join(BASE, "translations")


def create_app(config_name: str="default",
               db: object=db,
               name: str=APP_NAME) -> Flask:
    app = Flask(name or __name__)
    app.config.from_object(configs[config_name])

    app.elasticsearch = None

    babel.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    pagedown.init_app(app)

    if app.config['SSL_REDIRECT']:
        sslify = SSLify(app)

    from web_client.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # from web_client.auth import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix="/auth")

    # from web_client.profile import bp as profile_bp
    # app.register_blueprint(profile_bp, url_prefix="/profile")

    # from web_client.blog import bp as blog_bp
    # app.register_blueprint(blog_bp, url_prefix="/blog")

    # from web_client.files import bp as files_bp
    # app.register_blueprint(files_bp, url_prefix="/files")

    # from web_client.generate import bp as generate_bp
    # app.register_blueprint(generate_bp)

    from web_client.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not (app.debug or app.testing or app.config['DEBUG']):
        enable_email_error_notifications(
            app,
            level=app.config['LOG_LEVEL'],
            fmt=app.config['LOG_FORMAT']
        )
    if app.config['LOG_TO_STDOUT']:
        enable_logging_to_stdout(
            app,
            level=app.config['LOG_LEVEL'],
            fmt=app.config['LOG_FORMAT']
        )
    if app.config['LOG_TO_FILE']:
        enable_logging_to_file(
            app,
            level=app.config['LOG_LEVEL'],
            fmt=app.config['LOG_FORMAT'],
            path=app.config['LOG_PATH'],
            filename=app.config['LOG_NAME'],
            max_bytes=app.config['LOG_MAXBYTES'],
            backup_count=app.config['LOG_BACKUPCOUNT']
        )
    return app


@babel.localeselector
def get_locale() -> str:
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from web_client import models
