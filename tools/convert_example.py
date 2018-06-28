import logging
import os

# suspend engine logs
logging.basicConfig(level=logging.ERROR)

from engine.boards import BOARDS
from engine.utils import PATHS
from engine.utils.prepare import Convertor


if __name__ == "__main__":
    FROM_FMT = "yml"
    TO_FMT = "json"

    # convert yml static content to json and save it in the same location
    for board in BOARDS:
        from_path = os.path.join(PATHS.STATIC, ".".join((board, FROM_FMT)))
        Convertor.convert(from_path, TO_FMT)
