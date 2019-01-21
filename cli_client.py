import logging
from argparse import ArgumentParser, Namespace

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s\t%(levelname)s\t%(message)s")

from engine import BOARDS, Board


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="")
    parser.add_argument('board', type=str, choices=BOARDS,
                        help="board type (from list of supported)")
    parser.add_argument('--name', '-n', type=str, default=None,
                        help="project name")
    parser.add_argument('--archive', '-a', action="store_true",
                        help="archive generated project")
    parser.add_argument('--path', '-p', type=str, default=None,
                        help="location to save generated project")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_argv()
    board = Board(args.board).setup(project_name=args.name).generate()
    if args.archive:
        _ = board.archive(path=args.path)
    else:
        _ = board.dump(path=args.path)
