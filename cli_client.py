import json
import logging
import os
from argparse import ArgumentParser, Namespace
from enum import Enum
from typing import Any, Dict, Iterable, NoReturn

from engine import BOARDS, MIPS, Board
from engine.exceptions import InvalidProjectName


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s\t%(levelname)s\t%(message)s")


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="")
    parser.add_argument('board', type=str, choices=BOARDS,
                        metavar="BOARD NAME",
                        help=f"target board type, one of the following: "
                             f"{', '.join(BOARDS)}")
    parser.add_argument('--name', '-n', type=str, default=None,
                        metavar="PROJECT NAME",
                        help="name for generated project")
    parser.add_argument('--archive', '-a', action="store_true",
                        help="archive generated project")
    parser.add_argument('--path', '-p', type=str, default=None,
                        help="location to save generated project")
    parser.add_argument('--mips', '-m', type=str, default=None,
                        metavar="SCHOOL MIPS VERSION", choices=MIPS.VERSIONS,
                        help=f"specify which version of SchoolMIPS to include,"
                             f" one of the following: "
                             f"{', '.join(MIPS.VERSIONS)}")
    parser.add_argument('--config', '-c', type=str, default=None,
                        help="path to json file with board config")
    return parser.parse_args()


class ReturnCode(Enum):
    OK = 0
    CONFIG_ERROR = 3
    INVALID_PROJECT_NAME = 5
    UNKNOWN_ERROR = 255


class Config(object):
    def __init__(self,
                 config: str,
                 project_name: str=None,
                 mips_type: str=None,
                 path: str=None) -> NoReturn:
        self.configs = None
        self.functions = None
        self.functions_params = None
        self.errors = []
        self.project_name = project_name
        self.mips_type = mips_type

        if not config:
            logging.debug("No configs loaded.")
            return

        if not os.path.exists(config):
            self.errors.append(f"Config isn't found at '{config}'!")
            return

        with open(config) as fin:
            data = json.load(fin)
            self.configs = self._to_dict(data.get("conf", []))
            self.functions = self._to_dict(data.get("func", []))
            self.functions_params = data.get("params", {})

    @property
    def ok(self) -> bool:
        return not self.errors

    @staticmethod
    def _to_dict(items: Iterable[Any]) -> Dict[Any, bool]:
        return {k: v for k, v in
                zip(items, (True for _ in range(len(items))))}


def generate_board_and_save(board_name: str,
                            config: Config,
                            path_to_save: str = None,
                            archive: bool=False) -> NoReturn:
    board = Board(board_name).setup(
        project_name=config.project_name,
        mips_type=config.mips_type,
        flt=config.configs,
        conf=config.functions_params,
        func=config.functions
    ).generate()

    if archive:
        _ = board.archive(path=path_to_save)
    else:
        _ = board.dump(path=path_to_save)


def main(args: Namespace) -> ReturnCode:
    config = Config(args.config, args.name, args.mips)
    if not config.ok:
        for error in config.errors:
            logging.error(error)
        return ReturnCode.CONFIG_ERROR

    try:
        generate_board_and_save(args.board, config, args.path, args.archive)
    except InvalidProjectName as e:
        logging.error("%s", e)
        return ReturnCode.INVALID_PROJECT_NAME
    except BaseException as e:
        logging.error("%s", e)
        return ReturnCode.UNKNOWN_ERROR

    return ReturnCode.OK


if __name__ == "__main__":
    args = parse_argv()
    result = main(args)
    logging.debug("Exit with result: %s(%s)", result.name, result.value)
    exit(result.value)
