from web_client import cli, create_app, db
from web_client.models import Comment, File, Image, Post, User

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
        'Post': Post,
        'User': User
    }
