import logging
import os
import shutil
from contextlib import contextmanager
from typing import Generator, NoReturn

from jinja2 import FileSystemLoader

from fpga_marsohod_generator_engine.constants import MIPS
from fpga_marsohod_generator_engine.utils.render import ENV


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s "
    "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S"
)

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
MOCK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock")
MOCK_CONFIG = os.path.join(MOCK_DIR, "static-board.yml")
MOCK_MIPS_CONFIG = os.path.join(MOCK_DIR, "mips.yml")
MOCK_TEMPL_NAME = "template.jinja"

MIPS.CONFIG = MOCK_CONFIG


def free_test_dir() -> NoReturn:
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.mkdir(TEST_DIR)


def remove_test_dir() -> NoReturn:
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    assert not os.path.exists(TEST_DIR)


@contextmanager
def use_test_dir() -> Generator:
    free_test_dir()
    yield TEST_DIR
    remove_test_dir()


def _test_static_content(data: object) -> NoReturn:
    assert data
    assert isinstance(data, dict)
    for key in ("qpf", "qsf", "sdc", "v", "func"):
        assert key in data


@contextmanager
def use_mock_loader() -> Generator:
    original_loader = ENV.loader
    logging.debug("Change original loader to mock")
    ENV.loader = FileSystemLoader(MOCK_DIR, encoding="utf-8")
    yield
    logging.debug("Rollback to original loader")
    ENV.loader = original_loader
