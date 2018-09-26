import os

from werkzeug.contrib.profiler import ProfilerMiddleware

from web_client import create_app, db
from web_client.models import (Comment, Config, File, Image, Permission, Post,
                               Role, User)
from web_client.utils import cli


app = create_app()
cli.register(app)


if os.environ.get("FLASK_PROFILE"):
    app.config['PROFILE'] = True
    app.logger.info("Profiler is running")
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        restrictions=[30],  # length
        profile_dir=app.config.get("LOG_PATH")
    )


@app.shell_context_processor
def make_shell_context() -> dict:
    return {
        'app': app,
        'db': db,
        'Comment': Comment,
        'Config': Config,
        'File': File,
        'Image': Image,
        'Permission': Permission,
        'Post': Post,
        'Role': Role,
        'User': User
    }
