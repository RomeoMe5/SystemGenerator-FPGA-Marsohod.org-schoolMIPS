from flask import render_template, request, url_for
from werkzeug.urls import url_parse

from web_client import db
from web_client.errors import bp


@bp.errorhandler(404)
def not_found_error(error: object) -> tuple:
    prev_page = request.args.get("prev")
    if not prev_page or url_parse(prev_page).netloc:
        prev_page = url_for("main.index")
    return render_template("errors/404.html", prev_page=prev_page), 404


@bp.errorhandler(500)
def internal_error(error: object) -> tuple:
    db.session.rollback()
    prev_page = request.args.get("prev")
    if not prev_page or url_parse(prev_page).netloc:
        prev_page = url_for("main.index")
    return render_template("errors/500.html", prev_page=prev_page), 500
