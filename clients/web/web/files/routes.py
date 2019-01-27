import os
import re

from flask import (abort, current_app, flash, render_template, send_file,
                   url_for)
from flask_login import login_required

from fpga_marsohod_generator_engine.boards import BOARDS
from web_client import BASE_DIR, PATHS
from web_client.files import bp
from web_client.files.utils import decode_token, encode_to_token
from web_client.utils import INVALID_CHARS


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<uri>', methods=['GET', 'POST'])
@login_required
def files(uri: str = None) -> object:
    path = "." if uri is None else decode_token(uri)
    if path is None or INVALID_CHARS.search(path):
        current_app.logger.debug("[static] Can't open link: %s", path)
        return abort(404)
    files_path = os.path.join(PATHS.FILES, path)

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
