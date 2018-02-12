from web_client.app import APP, DB
from web_client.app.models import User


@APP.shell_context_processor
def make_shell_context() -> dict:
    return {'APP': APP, 'DB': DB, 'User': User}
