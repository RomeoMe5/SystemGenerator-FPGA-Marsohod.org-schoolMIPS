from web_client import create_app, db
from web_client.models import Comment, File, Image, Permissions, Post, User
from web_client.utils import cli


app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context() -> dict:
    return {
        'app': app,
        'db': db,
        'Comment': Comment,
        'File': File,
        'Image': Image,
        'Permissions': Permissions,
        'Post': Post,
        'User': User
    }
