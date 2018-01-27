import logging
import os
from functools import wraps
from typing import Callable

from jinja2.environment import Environment, Template

from engine.utils import ENV


def load_template(template_path: str,
                  env: Environment=ENV,
                  fallback_format: str="jinja") -> Callable:
    """
        Load template and pass it as named argument 'template' to function

        Doesn't handle exceptions.
    """
    def decor(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> object:
            path = template_path
            if not os.path.exists(path) and not path.endswith(fallback_format):
                logging.debug(
                    "'%s' isn't exists! Trying to find '%s' alternative",
                    path,
                    fallback_format
                )
                path = ".".join((path, fallback_format))
                if not os.path.exists(path):
                    logging.error("Can't find template: '%s'!", path)
                    raise FileNotFoundError(f"'{path}' isn't exists")
            logging.debug("Loading template '%s'...", path)
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
                company_name: str="HSE",  # @TODO: remove hardcoded HSE
                file_type: str=None,
                **kwargs) -> object:
        if not file_type:
            file_type = func.__name__
            logging.debug("Assume file type is '%s'.", file_type)
        return func(
            *args,
            company_name=company_name,
            file_type=file_type,
            **kwargs
        )
    return wrapper
