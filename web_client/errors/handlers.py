from flask import current_app, render_template, request, url_for
from werkzeug.urls import url_parse

from web_client import db
from web_client.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error: object) -> tuple:
    # current_app.logger.debug("Page not found: %s", error)
    prev_page = request.args.get("prev")
    if not prev_page or url_parse(prev_page).netloc:
        return render_template("errors/404.html"), 404
    return render_template("errors/404.html", prev_page=prev_page), 404


@bp.app_errorhandler(500)
def internal_error(error: object) -> tuple:
    db.session.rollback()
    # current_app.logger.error("Internal error occured: %s", error)
    prev_page = request.args.get("prev")
    if not prev_page or url_parse(prev_page).netloc:
        return render_template("errors/500.html"), 500
    return render_template("errors/500.html", prev_page=prev_page), 500
