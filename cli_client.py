import json
import logging
import os
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, Iterable, NoReturn

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s\t%(levelname)s\t%(message)s")

from engine import BOARDS, MIPS, Board


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


class Config(object):
    def __init__(self, config: str) -> NoReturn:
        self.configs = None
        self.functions = None
        self.errors = None
        if not config:
            return
        if not os.path.exists(config):
            logging.ERROR(f"Config isn't found at '{args.config}'!")
        with open(config) as fin:
            data = json.load(fin)
            self.configs = self._to_dict(data.get("configs", []))
            self.functions = self._to_dict(data.get("functions", []))

    @property
    def ok(self) -> bool:
        return self.errors is None

    @staticmethod
    def _to_dict(items: Iterable[Any]) -> Dict[Any, bool]:
        return {k: v for k, v in
                zip(items, (True for _ in range(len(items))))}


def main() -> int:
    args = parse_argv()

    config = Config(args.config)
    if config.errors:
        return 1

    board = Board(args.board)
    _ = board.setup(
        project_name=args.name,
        mips_type=args.mips,
        flt=config.configs,
        func=config.functions
    )
    _ = board.generate()

    if args.archive:
        _ = board.archive(path=args.path)
    else:
        _ = board.dump(path=args.path)

    return 0


if __name__ == "__main__":
    exit(main())
