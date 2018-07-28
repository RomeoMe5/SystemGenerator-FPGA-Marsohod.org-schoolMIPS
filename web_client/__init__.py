import os

from flask import Flask, current_app, request
from flask_babel import lazy_gettext as _l
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from configs.web_client import Config
from web_client.log import (enable_email_error_notifications,
                            enable_logging_to_file, enable_logging_to_stdout)

babel = Babel()
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
moment = Moment()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = _l("Please log in to access this page.")

BASE_DIR = os.path.dirname(__file__)
STATIC_PATH = os.path.join(BASE_DIR, "static")
POSTS_PATH = os.path.join(STATIC_PATH, "posts")
FILES_PATH = os.path.join(STATIC_PATH, "files")


def create_app(config_class: object=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    babel.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)

    from web_client.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from web_client.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from web_client.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix="/profile")

    from web_client.blog import bp as blog_bp
    app.register_blueprint(blog_bp, url_prefix="/blog")

    # from web_client.files import bp as files_bp
    # app.register_blueprint(files_bp, url_prefix="/files")

    # from web_client.generate import bp as generate_bp
    # app.register_blueprint(generate_bp)

    from web_client.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing and not app.config['DEBUG']:
        enable_email_error_notifications(
            app,
            app.config['LOG_LEVEL'],
            app.config['LOG_FORMAT']
        )
    if app.config['LOG_TO_STDOUT']:
        enable_logging_to_stdout(
            app,
            app.config['LOG_LEVEL'],
            app.config['LOG_FORMAT']
        )
    else:
        enable_logging_to_file(
            app,
            app.config['LOG_LEVEL'],
            app.config['LOG_FORMAT'],
            app.config['LOG_PATH'],
            app.config['LOG_NAME'],
            app.config['LOG_MAXBYTES'],
            app.config['LOG_BACKUPCOUNT']
        )

    return app


@babel.localeselector
def get_locale() -> str:
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from web_client import models
