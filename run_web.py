from web_client import cli, create_app, db
from web_client.models import Notification, Task, User


app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context() -> dict:
    return {
        'app': app,
        'db': db,
        'User': User,
        'Notification': Notification,
        'Task': Task
    }
