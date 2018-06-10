import os
import re
from urllib import parse

from flask import (abort, current_app, flash, render_template, send_file,
                   url_for)
from flask_login import login_required

from engine.boards import BOARDS
from web_client import BASE_DIR
from web_client.files import bp
from web_client.files.utils import decode_token, encode_to_token

FILES_BASE_PATH = os.path.join(BASE_DIR, os.path.join("static", "files"))
FORBIDEN_SYMBOLS = re.compile(r"[\\<>[\]?:*\"|]")


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<path>', methods=['GET', 'POST'])
@login_required
def static(path: str = None) -> object:
    path = "." if path is None else decode_token(path)
    if path is None or FORBIDEN_SYMBOLS.search(path):
        current_app.logger.debug("[static] Can't open link: %s", path)
        return abort(404)
    files_path = os.path.join(FILES_BASE_PATH, path)

    if os.path.isfile(files_path):
        current_app.logger.debug("[static] send file: %s", files_path)
        return send_file(
            files_path,
            mimetype="application/octet-stream",
            as_attachment=True,
            attachment_filename=os.path.split(path)[-1]
        )

    files = []
    if path != ".":
        files.append(("..", "", "", url_for(
            "files.static", path=encode_to_token(os.path.dirname(path))
        )))
    for file_name in os.listdir(files_path):
        file_path = os.path.join(files_path, file_name)
        is_dir = os.path.isdir(file_path)
        files.append((
            file_name,
            "directory" if is_dir else "file",
            "" if is_dir else str(os.path.getsize(file_path)) + " bytes",
            url_for("files.static",
                    path=encode_to_token("/".join((path, file_name))))
        ))

    return render_template(
        "files/static.html",
        title=path[1:] if path != "." else "/",
        files=files,
        boards=BOARDS
    )
