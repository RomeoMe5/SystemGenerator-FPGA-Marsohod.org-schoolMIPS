from collections import Callable
from functools import wraps

from jinja2.environment import Environment, Template


def load_template(path: str, env: Environment) -> Callable:
    """
        Load template and pass it as named argument 'template' to function

        Doesn't handle exceptions.
    """
    def decor(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> object:
            return func(*args, template=env.get_template(path), **kwargs)
        return wrapper
    return decor


def default_args_for_render(func: Callable) -> Callable:
    """
        Pass common arguments for all render functions

        Doesn't handle exceptions.
    """
    @wraps(func)
    def wrapper(*args,
                company_name: str="HSE",
                file_type: str=None,
                **kwargs) -> object:
        if not file_type:
            file_type = func.__name__.split('_')[-1]
        return func(
            *args,
            company_name=company_name,
            file_type=file_type,
            **kwargs
        )
    return wrapper
