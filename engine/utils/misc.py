from functools import wraps
from typing import Callable


def none_safe(args: bool=True, kwargs: bool=True) -> Callable:
    """
        Pass only not None args/kwargs to function
        Doesn't handle exceptions.
    """
    def decor(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*_args, **_kwargs) -> object:
            if args:
                _args = [arg for arg in _args if arg is not None]
            if kwargs:
                _kwargs = {k: v for k, v in _kwargs.items() if v is not None}
            return func(*_args, **_kwargs)
        return wrapper
    return decor
