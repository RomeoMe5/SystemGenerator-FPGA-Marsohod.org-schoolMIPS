import os
from collections import Callable
from functools import wraps

try:
    from engine_config import LOGGER  # global config logger import
except ImportError as err:
    # default logging configuration
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

    LOGGER.warning(err)


def log(func: Callable) -> Callable:
    """ Logging function/method behavior """

    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        LOGGER.debug("ENTER(%s)", func.__name__)
        for arg in args:
            LOGGER.debug("ARG::%s", arg)
        for key, value in kwargs.items():
            LOGGER.debug("KWARG::%s=%s", key, value)
        result = func(*args, **kwargs)
        LOGGER.debug("EXIT(%s)::%s", func.__name__, result)
        return result
    return wrapper
