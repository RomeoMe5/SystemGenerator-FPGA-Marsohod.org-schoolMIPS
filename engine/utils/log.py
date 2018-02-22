import os
from collections import Callable
from functools import wraps

try:
    from configs.engine import LOGGER
except ImportError as err:
    import logging
    logging.basicConfig(
        level=logging.WARNING,
        format="[%(asctime)s] %(levelname)s "
               "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%H:%M:%S"
    )
    LOGGER = logging.getLogger('$default.log')


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
