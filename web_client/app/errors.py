from flask import render_template, request, url_for
from werkzeug.urls import url_parse

from web_client.app import APP, DB


@APP.errorhandler(404)
def not_found_error(error: object) -> tuple:
    prev_page = request.args.get("prev")
    if not prev_page or url_parse(prev_page).netloc:  # @RMB: .netloc != ''
        prev_page = url_for("index")
    return render_template("404.html", prev_page=prev_page), 404


@APP.errorhandler(500)
def internal_error(error: object) -> tuple:
    DB.session.rollback()
    prev_page = request.args.get("prev")
    if not prev_page or url_parse(prev_page).netloc:  # @RMB: .netloc != ''
        prev_page = url_for("index")
    return render_template("500.html", prev_page=prev_page), 500
