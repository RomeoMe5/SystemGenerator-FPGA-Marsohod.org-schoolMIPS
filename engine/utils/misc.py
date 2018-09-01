from functools import wraps
from typing import Any, Callable

from engine.utils.globals import LOGGER


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


def none_safe(to_args: bool=True, to_kwargs: bool=True) -> Callable:
    """
        Pass only not None args/kwargs to function
        Doesn't handle exceptions.
    """
    def decor(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if to_args:
                args = [arg for arg in args if arg is not None]
            if to_kwargs:
                kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return func(*args, **kwargs)
        return wrapper
    return decor
