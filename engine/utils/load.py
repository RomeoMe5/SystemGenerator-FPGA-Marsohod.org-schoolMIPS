""" Data loaders """

import json
import logging
import os

from engine.utils import Config


def get_static_path(filename: str,
                    extension: str=Config.STATIC_EXTENSION,
                    path_to_static: str=Config.PATHS['static']) -> str:
    """ Return path for static object (if it exists) """
    path = os.path.join(path_to_static, filename)

    if extension and not filename.endswith(extension):
        logging.debug("Update filename with '%s' extension.", extension)
        path = ".".join((path, extension))

    if not os.path.exists(path):
        logging.error("'%s' isn't exists!", path)
        raise FileNotFoundError(f"'{path}' isn't exists!")

    return path


def load_json(filepath: str,
              encoding: str=Config.FILE_ENCODING,
              errors: str=Config.FILE_ERRORS) -> dict:
    """ Loads json contents """
    if not os.path.exists(filepath):
        logging.error("File isn't exists '%s'!", filepath)

    with open(filepath, 'r', encoding=encoding, errors=errors) as fin:
        logging.debug("Loading '%s' content...", filepath)
        return json.load(fin)


def load_plain_text(filepath: str,
                    as_str: bool=True,
                    encoding: str=Config.FILE_ENCODING,
                    errors: str=Config.FILE_ERRORS) -> str or list:
    """ Loads plain text file contents as string or list of strings """
    if not os.path.exists(filepath):
        logging.error("File isn't exists '%s'!", filepath)

    with open(filepath, 'r', encoding=encoding, errors=errors) as fin:
        logging.debug("Loading '%s' content...", filepath)
        if as_str:
            return fin.read()
        else:
            return fin.readlines()
