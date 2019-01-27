import os

from flask import (abort, current_app, flash, render_template, request,
                   send_file)
from flask_login import current_user

import fpga_marsohod_generator_engine.boards
from fpga_marsohod_generator_engine.boards import BOARDS
from web_client import db
from web_client.generate import bp, forms
from web_client.utils import get_random_str


@bp.route('/board/<board>', methods=['GET', 'POST'])
def board(board: str) -> object:
    try:
        form = getattr(forms, board + "Form")()
        board = getattr(fpga_marsohod_generator_engine.boards, board)()
    except BaseException as exc:
        current_app.logger.warning("Can't find board %s:\n%s", board, exc)
        return abort(404)

    if board.message:
        flash(board.message)

    if form.validate_on_submit():
        params = request.form.copy()
        _ = params.pop("submit", None)
        _ = params.pop("csrf_token", None)

        if current_user.is_anonymous:
            path = os.path.join(current_app.config['STATIC_PATH'],
                                get_random_str())
            if not os.path.exists(path):
                os.mkdir(path)
        else:
            path = current_user.path
        project_path = os.path.join(path, params['project_name'])
        board.generate(**params).archive(project_path=project_path)
        # BUG remove directory after files generation

        fmt = "tar"
        return send_file(
            ".".join((project_path, fmt)),
            mimetype="application/octet-stream",
            as_attachment=True,
            attachment_filename=".".join((params['project_name'], fmt))
        )

    return render_template(
        "generate/board.html",
        form=form,
        title=board.__class__.__name__,
        boards=BOARDS
    )
