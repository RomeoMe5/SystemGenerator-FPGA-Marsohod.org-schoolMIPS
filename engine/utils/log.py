import os
from functools import wraps
from typing import Any, Callable

try:
    from engine_config import LOGGER
except ImportError as exc:
    import logging
    from logging.handlers import RotatingFileHandler
    from engine.utils.globals import PATHS

    LOG_LEVEL = logging.WARNING
    LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s." \
                 "{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s"
    LOG_NAME = "$default.log"
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt="%H:%M:%S")
    LOGGER = logging.getLogger(LOG_NAME)
    FILE_HANDLER = RotatingFileHandler(
        os.path.join(PATHS.BASE, LOG_NAME),
        maxBytes=1024 * 100,
        backupCount=10
    )
    FILE_HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))
    FILE_HANDLER.setLevel(LOG_LEVEL)
    LOGGER.addHandler(FILE_HANDLER)

    LOGGER.debug(exc)


def log(func: Callable) -> Callable:
    """ Logging function/method behavior """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        LOGGER.debug("<%s> ENTER", func.__name__)
        for arg in args:
            LOGGER.debug("<%s> ARG  \t%s", func.__name__, arg)
        for key, value in kwargs.items():
            LOGGER.debug("<%s> KWARG\t%s=%s", func.__name__, key, value)
        result = func(*args, **kwargs)
        LOGGER.debug("<%s> EXIT \t%s", func.__name__, result)
        return result
    return wrapper
