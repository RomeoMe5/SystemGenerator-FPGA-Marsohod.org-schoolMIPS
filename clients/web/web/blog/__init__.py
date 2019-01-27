from flask import Blueprint

from web_client.models import Permission


bp = Blueprint("blog", __name__)


@bp.app_context_processor
def inject_permissions() -> dict:
    return dict(Permission=Permission)


from web_client.blog import routes
