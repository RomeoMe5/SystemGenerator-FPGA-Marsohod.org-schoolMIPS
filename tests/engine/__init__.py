import asyncio
import os
from contextlib import contextmanager
from typing import Generator, NoReturn

from jinja2 import FileSystemLoader

from engine.utils.render import ENV


MOCK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock")
MOCK_CONFIG = os.path.join(MOCK_DIR, "static-board.yml")
MOCK_TEMPL_NAME = "template.jinja"
MOCK_FUNC_TEMPL_NAME = "func.jinja"


def _test_static_content(data: object) -> NoReturn:
    assert data
    assert isinstance(data, dict)
    for key in ("qpf", "qsf", "sdc", "v", "func"):
        assert key in data


@contextmanager
def use_mock_loader() -> Generator:
    original_loader = ENV.loader
    ENV.loader = FileSystemLoader(MOCK_DIR, encoding="utf-8")
    yield
    ENV.loader = original_loader


@contextmanager
def get_event_loop() -> Generator:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
    del loop
