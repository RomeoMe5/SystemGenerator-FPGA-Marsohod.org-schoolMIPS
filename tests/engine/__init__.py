import asyncio
import os
from contextlib import contextmanager
from typing import Generator, NoReturn

from jinja2 import FileSystemLoader

from engine.utils.render import ENV
from tests import logging


MOCK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock")
MOCK_CONFIG = os.path.join(MOCK_DIR, "static-board.yml")
MOCK_TEMPL_NAME = "template.jinja"


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


@contextmanager
def get_event_loop() -> Generator:
    loop = asyncio.new_event_loop()
    logging.debug("Set new event loop: %s", loop)
    asyncio.set_event_loop(loop)
    yield loop
    logging.debug("Close and remove event loop: %s", loop)
    loop.close()
    del loop
