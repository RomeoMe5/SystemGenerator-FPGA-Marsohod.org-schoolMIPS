"""
    Convert yml static configs to json for each board
    and save it in the same location
"""

import logging
import os

# suspend engine logs
logging.basicConfig(level=logging.ERROR)

from engine import BOARDS
from engine.utils import PATHS
from engine.utils.prepare import Convertor


if __name__ == "__main__":
    FROM_FMT = "yml"

    # it's possible specify project name as first script's positional argument
    TO_FMT = "json" if len(sys.argv) < 2 else sys.argv[1].lower()

    for board in BOARDS:
        from_path = os.path.join(PATHS.STATIC, ".".join((board, FROM_FMT)))
        Convertor.convert(from_path, TO_FMT)
