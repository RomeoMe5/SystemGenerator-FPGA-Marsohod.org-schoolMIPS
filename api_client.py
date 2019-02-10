import io
import logging
import os
from argparse import ArgumentParser, Namespace
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Iterable, NoReturn, Tuple

from flask import Flask, Response, jsonify, make_response, request
from flask_sslify import SSLify
from werkzeug.contrib.profiler import ProfilerMiddleware

from engine import BOARDS, FUNCTIONS, MIPS, Board
from engine.exceptions import InvalidProjectName


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
    app = Flask(name or __name__)
    app.config.from_object(config)

    if app.config['SSL_REDIRECT']:
        sslify = SSLify(app)

    return app


app = create_app(AppConfig, "api-client")


class ErrorCode(Enum):
    UNKNOWN_ERROR = 600
    INVALID_CONFIG = 601
    INVALID_PROJECT_NAME = 602
    UNSUPPORTED_BOARD = 603


class Config(object):
    CONFIG_SHEMA = {
        'board': str,
        'mips': str,
        'name': str,
        'conf': list,
        'func': list,
        'params': dict
    }

    def __init__(self, data: dict) -> NoReturn:
        self.board = data['board']
        self.mips_type = data.get("mips")
        self.project_name = data.get("name")
        self.configs = self._to_dict(data.get("conf", []))
        self.functions = self._to_dict(data.get("func", []))
        self.functions_params = data.get("params", {})

    @staticmethod
    def validate_config(data: dict) -> str or None:
        if "board" not in data:
            return "Missing required parameter 'board'"
        for key, val in data.items():
            if key not in Config.CONFIG_SHEMA:
                return f"Invalid key '{key}'"
            if not isinstance(val, Config.CONFIG_SHEMA[key]):
                return f"Invalid value type '{type(val)}' for key '{key}'"

    @staticmethod
    def _to_dict(items: Iterable[Any]) -> Dict[Any, bool]:
        return {k: v for k, v in
                zip(items, (True for _ in range(len(items))))}


def create_error_response(code: ErrorCode,
                          description: str) -> Tuple[Response, int]:
    logging.error("%s (%s): '%s'", code.name, code.value, description)
    return jsonify({
        'name': code.name,
        'info': description
    }), 405


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


@app.route("/generate", methods=["GET", "POST"])
def generate() -> Response:
    """
        API
        ===

        Returns generated files as internal representation (json object)
            for POST requests.

        Required
        --------
        * board: str - one of supported boards model

        Optional
        --------
        * name: str - project name
        * mips: str - version of SchoolMIPS core
        * conf: List[str] - board configuration
        * func: List[str] - functions to include
        * params: Dict[str, int] - functions configurations
    """
    params = request.args

    validation_result = Config.validate_config(params)
    if validation_result is not None:
        return create_error_response(
            ErrorCode.INVALID_CONFIG,
            description=validation_result
        )

    try:
        board = get_configured_board(Config(params))
    except InvalidProjectName as e:
        return create_error_response(ErrorCode.INVALID_PROJECT_NAME, str(e))
    except BaseException as e:
        return create_error_response(ErrorCode.UNKNOWN_ERROR, str(e))

    if request.method == "POST":
        return jsonify(board.configs)
    return send_archive(board.as_archive, f"{board.project_name}.tar")


@app.route("/boards")
def boards() -> Response:
    return jsonify({'supported boards': BOARDS})


@app.route("/board/<board>")
@lru_cache()
def board(board: str) -> Response:
    if board not in BOARDS:
        return create_error_response(
            ErrorCode.UNSUPPORTED_BOARD,
            description=f"There is no '{board}' in supported list: {BOARDS}"
        )
    return jsonify({'board': board, 'params': Board(board).params})


@app.route("/mips")
def mips() -> Response:
    return jsonify({'supported mips types': MIPS.VERSIONS})


@app.route("/functions")
def functions() -> Response:
    return jsonify({
        'supported functions': FUNCTIONS.ITEMS,
        'configurations': FUNCTIONS.PARAMS
    })


def get_response_from_error(error: Exception) -> Tuple[Response, int]:
    return jsonify({
        'name': error.name,
        'info': error.description
    }), error.code


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
    parser = ArgumentParser(description="Starter for API client")
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
