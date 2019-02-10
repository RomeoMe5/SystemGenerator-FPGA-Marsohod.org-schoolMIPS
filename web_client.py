import io
import logging
import os
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, Iterable, NoReturn, Tuple

from flask import (Flask, Response, abort, flash, make_response, redirect,
                   render_template, request, url_for)
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify
from flask_wtf import FlaskForm
from werkzeug.contrib.profiler import ProfilerMiddleware
from wtforms import (BooleanField, SelectField, SelectMultipleField,
                     StringField, SubmitField)
from wtforms.validators import DataRequired, Optional, ValidationError

from engine import BOARDS, FUNCTIONS, MIPS, Board
from engine.utils.prepare import validate_project_name


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)d "
           "[%(name)s:%(filename)s.%(funcName)s:%(lineno)d] "
           "%(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)


class AppConfig(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "no-one-knows"
    SSL_REDIRECT = True  # NOTE not working in debug mode


def create_app(config: AppConfig, name: str=None) -> Flask:
    current_folder = os.path.dirname(__file__)
    app = Flask(
        name or __name__,
        template_folder=current_folder,
        static_folder=current_folder
    )
    app.config.from_object(config)

    bootstrap = Bootstrap()
    bootstrap.init_app(app)

    if app.config['SSL_REDIRECT']:
        sslify = SSLify(app)

    return app


app = create_app(AppConfig, "web-client")


class BoardForm(FlaskForm):
    name = StringField(
        "Project Name",
        default="MyFpgaProject",
        description="Should contains only letters, numbers and underscores",
        validators=[DataRequired()],
        id="board-form-name"
    )
    conf = SelectMultipleField(
        "Board configurations",
        validators=[Optional()],
        id="board-form-enable-conf"
    )
    enable_mips = BooleanField(
        "Include SchoolMIPS core to generated project",
        default=False,
        validators=[Optional()],
        id="board-form-enable-mips"
    )
    mips = SelectField(
        "Version of SchoolMIPS core",
        choices=tuple((v, v) for v in MIPS.VERSIONS),
        validators=[Optional()],
        id="board-form-mips"
    )
    func = SelectMultipleField(
        "Additional functions",
        choices=tuple(FUNCTIONS.ITEMS.items()),
        validators=[Optional()],
        id="board-form-enable-func"
    )
    # TODO params
    submit = SubmitField("Generate", id="form-submit-button")

    def validate_name(self, name: StringField) -> NoReturn:
        name = name.data.strip()
        if not validate_project_name(name):
            logging.debug(f"Invalid project name '{name}'")
            raise ValidationError(f"Invalid project name '{name}'")


class Config(object):
    def __init__(self, board: str, form: BoardForm) -> NoReturn:
        self.board = board
        self.mips_type = form.mips.data if form.enable_mips.data else None
        self.project_name = form.name.data.strip()
        self.configs = self._to_dict(form.conf.data)
        self.functions = self._to_dict(form.func.data)
        self.functions_params = {}  # TODO

    @staticmethod
    def _to_dict(items: Iterable[Any]) -> Dict[Any, bool]:
        return {k: v for k, v in
                zip(items, (True for _ in range(len(items))))}


def get_configured_board(config: Config) -> Board:
    return Board(config.board).setup(
        project_name=config.project_name,
        mips_type=config.mips_type,
        flt=config.configs,
        conf=config.functions_params,
        func=config.functions
    ).generate()


def send_archive(content: io.BytesIO, filename: str) -> Response:
    response = make_response(content.getvalue())
    response.headers['Content-Type'] = "application/octet-stream"
    response.headers['Content-Disposition'] = \
        f"attachment; filename={filename}"
    return response


@app.route("/", methods=["GET", "POST"])
def index() -> Response:
    board = request.args.get("board", "").lower()

    form = None
    if board in BOARDS:
        form = BoardForm()
        form.conf.choices = ((v, v) for v in Board(board).params.keys())

        if form.validate_on_submit():
            try:
                board = get_configured_board(Config(board, form))
            except BaseException as e:
                logging.error("Generation failed with exception: %s", e)
                abort(500)

            return send_archive(board.as_archive, f"{board.project_name}.tar")
    elif board:
        flash(f"No such board '{board}' supported")
        return redirect(url_for("index"))

    return render_template(
        "web_client.jinja",
        form=form,
        board=board,
        boards=BOARDS
    )


@app.route("/img/board")
def board_picture() -> Response:
    return app.send_static_file("board.svg")


def get_response_from_error(error: Exception) -> Tuple[Response, int]:
    return error.get_response(), error.code


@app.errorhandler(401)
def unauthorized(error: Exception) -> Tuple[Response, int]:
    return get_response_from_error(error)


@app.errorhandler(403)
def forbidden(error: Exception) -> Tuple[Response, int]:
    return get_response_from_error(error)


@app.errorhandler(404)
def not_found(error: Exception) -> Tuple[Response, int]:
    return get_response_from_error(error)


@app.errorhandler(405)
def method_not_allowed(error: Exception) -> Tuple[Response, int]:
    return get_response_from_error(error)


@app.errorhandler(500)
def internal_server_error(error: Exception) -> Tuple[Response, int]:
    return get_response_from_error(error)


@app.errorhandler(501)
def not_implemented(error: Exception) -> Tuple[Response, int]:
    return get_response_from_error(error)


@app.shell_context_processor
def make_shell_context() -> dict:
    return {
        'app': app,
        'Board': Board
    }


def enable_profiling(app: Flask, path: str) -> NoReturn:
    if not os.path.exists(path):
        logging.info(f"Create '{path}'.")
        os.mkdir(path)

    app.config['PROFILE'] = True
    logging.warning("Profiler is running!")
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        restrictions=[30],  # length
        profile_dir=path
    )


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="Starter for WEB client")
    parser.add_argument('host', type=str, default=None, nargs="?")
    parser.add_argument('--port', '-p', type=int, default=None)
    parser.add_argument('--debug', '-d', action="store_true")
    parser.add_argument('--profile', '-P', action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_argv()

    if args.profile:
        enable_profiling(app, path="perf-logs")

    app.run(host=args.host, port=args.port, debug=args.debug)

    return 0


if __name__ == "__main__":
    exit(main())
