import logging
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, Iterable, NoReturn, Tuple

from flask import Flask, Response, abort, jsonify, request, send_file

from engine import BOARDS, FUNCTIONS, MIPS, Board
from engine.exceptions import InvalidProjectName


app = Flask(__name__)


class Config(object):
    CONFIG_SHEMA = {
        'board': str,
        'mips': str,
        'name': str,
        'conf': list,
        'func': list,
        'plain': object
    }

    def __init__(self, data: dict) -> NoReturn:
        self.board = data['board']
        self.mips_type = data.get("mips")
        self.project_name = data.get("name")
        self.configs = self._to_dict(data.get("conf", []))
        self.functions = self._to_dict(data.get("func", []))

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


def create_error_response(code: int,
                          name: str,
                          description: str) -> Tuple[Response, int]:
    logging.error("%s (%s): '%s'", name, code, description)
    return jsonify({
        'name': name,
        'info': description
    }), 405


def get_configured_board(config: Config) -> Board:
    return Board(config.board).setup(
        project_name=config.project_name,
        mips_type=config.mips_type,
        flt=config.configs,
        func=config.functions
    ).generate()


@app.route("/")
def ping() -> Response:
    if request.args:
        abort(405)
    return jsonify(0)


@app.route("/generate", methods=["POST"])
def generate() -> Response:
    """
        API params
        ==========

        Required
        --------
        * board: str - board model

        Optional
        --------
        * name: str - project name
        * mips: str - SchoolMIPS version
        * conf: List[str] - board configuration
        * func: List[str] - functions to include
    """
    params = request.args

    validation_result = Config.validate_config(params)
    if validation_result is not None:
        return create_error_response(
            code=601,
            name="Invalid config",
            description=validation_result
        )

    try:
        board = get_configured_board(Config(params))
    except InvalidProjectName as e:
        return create_error_response(
            code=602,
            name="Invalid project name",
            description=str(e)
        )
    except BaseException as e:
        return create_error_response(
            code=600,
            name="Unknown error",
            description=str(e)
        )

    if params.get("plain"):
        return jsonify(board.configs)
    return send_file(
        board.as_archive,
        mimetype="application/octet-stream",
        as_attachment=True,
        attachment_filename=f"{board.project_name}.tar"
    )


@app.route("/boards")
def boards() -> Response:
    return jsonify({'supported boards': BOARDS})


@app.route("/mips")
def mips() -> Response:
    return jsonify({'supported mips types': MIPS.VERSIONS})


@app.route("/functions")
def functions() -> Response:
    return jsonify({'supported functions': FUNCTIONS})


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


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="")
    parser.add_argument('host', type=str, default=None, nargs="?")
    parser.add_argument('--port', '-p', type=int, default=None)
    parser.add_argument('--debug', '-d', action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_argv()
    app.run(host=args.host, port=args.port, debug=args.debug)
