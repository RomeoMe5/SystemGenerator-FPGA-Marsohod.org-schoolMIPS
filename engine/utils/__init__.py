""" Utils """

import logging
import os
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape

import engine


class Config(object):
    """ Configuration storage """

    PATHS = {'root': os.path.dirname(engine.__file__)}
    PATHS['static'] = os.path.join(PATHS['root'], "static")
    PATHS['templ'] = os.path.join(PATHS['root'], "templates")

    FILE_ENCODING = os.environ.get("FILE_ENCODING", "utf-8")
    FALLBACK_EXTENSION = os.environ.get("FALLBACK_EXTENSION", "jinja")
    COPYRIGHT = os.environ.get("COPYRIGHT", "MUEM (HSE University)")

    ENV = Environment(
        loader=FileSystemLoader(PATHS['templ'], encoding=FILE_ENCODING),
        autoescape=select_autoescape(enabled_extensions=(), default=False),
        trim_blocks=True,
        lstrip_blocks=True,
        newline_sequence="\r\n" if "win" in sys.platform else "\n",
        keep_trailing_newline=True,
        auto_reload=False
    )

    def __init__(self, **kwargs) -> None:
        for key, val in kwargs.items():
            self[key] = val

    def get(self, key: str, placeholder: object=None) -> object:
        return self[key] or placeholder

    def __setitem__(self, key: str, item: object) -> None:
        if not isinstance(key, str):
            raise ValueError("Wrong key type '%s', expect str!", type(key))
        logging.debug("Adding configuration: '%s' = '%s'.", key, item)
        self.__dict__[key] = item

    def __getitem__(self, key: str) -> object:
        item = self.__dict__.get(key)

        if item is None:
            logging.debug("Geting config name '%s' on class level.", key)
            item = self.__class__.__dict__.get(key)

        if item is None:
            logging.debug("Can't find config name '%s'.", key)

        return item

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            logging.debug("Removing config '%s' from instance.", key)
            del self.__dict__[key]
        elif key in self.__class__.__dict__:
            logging.debug("Removing config '%s' from class.", key)
            del self.__class__.__dict__[key]
        else:
            logging.debug("Config '%s' is not found.", key)

    def __contains__(self, key: str) -> bool:
        is_found = key in self.__dict__
        if not is_found:
            is_found = key in self.__class__.__dict__
        return is_found
