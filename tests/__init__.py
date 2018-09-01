import logging
import os
import shutil
from typing import NoReturn


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s "
    "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S"
)

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")


def free_test_dir() -> NoReturn:
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.mkdir(TEST_DIR)


free_test_dir()
