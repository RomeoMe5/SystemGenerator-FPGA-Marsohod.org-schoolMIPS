from functools import wraps
from typing import Any, Callable


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
