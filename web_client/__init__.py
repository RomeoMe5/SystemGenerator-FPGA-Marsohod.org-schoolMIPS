import os

from flask import Flask, current_app, request
from flask_babel import lazy_gettext as _l
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from web_client.log import (enable_email_error_notifications,
                            enable_logging_to_file, enable_logging_to_stdout)
from web_client_config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bootstrap = Bootstrap()
babel = Babel()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = _l("Please log in to access this page.")

BASE_DIR = os.path.dirname(__file__)


def create_app(config_class: object=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)
    login_manager.init_app(app)

    from web_client.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from web_client.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from web_client.blog import bp as blog_bp
    app.register_blueprint(blog_bp, url_prefix="/article")

    from web_client.files import bp as files_bp
    app.register_blueprint(files_bp, url_prefix="/files")

    from web_client.generate import bp as generate_bp
    app.register_blueprint(generate_bp)

    from web_client.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        enable_email_error_notifications(app)
        if app.config['LOG_TO_STDOUT']:
            enable_logging_to_stdout(app)
        else:
            enable_logging_to_file(app)

    return app


@babel.localeselector
def get_locale() -> str:
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from web_client import models
