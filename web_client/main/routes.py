import os
from datetime import datetime

from flask import (abort, current_app, g, redirect, render_template, request,
                   send_file, url_for)
from flask_babel import get_locale
from flask_login import current_user, login_required

import engine.boards
from engine.boards import BOARDS
from web_client import db
from web_client.main import bp, forms


@bp.before_request
def before_request() -> None:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/')
@login_required
def index() -> object:
    return redirect(url_for("main.board", board=BOARDS[0]))


@bp.route('/board/<board>', methods=['GET', 'POST'])
@login_required
def board(board: str) -> object:
    try:
        form = getattr(forms, board + "Form")()
    except BaseException as err:
        current_app.logger.warning("Can't find board %s:\n%s", board, err)
        return abort(404)

    if form.validate_on_submit():
        params = request.form.copy()
        params.pop('submit', None)
        params.pop('csrf_token', None)

        path = os.path.join(current_user.path, params['project_name'])
        board = getattr(engine.boards, board)()
        board.generate(**params).archive(project_path=path)

        fmt = "tar"
        return send_file(
            ".".join((path, fmt)),
            mimetype='application/octet-stream',
            as_attachment=True,
            attachment_filename=".".join((params['project_name'], fmt))
        )

    return render_template("board.html", form=form, title=board, boards=BOARDS)
