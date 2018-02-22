import json
import os

from engine.utils import PATHS
from engine.utils.log import LOGGER, log


def get_static_path(filename: str,
                    extension: str="json",
                    path_to_static: str=PATHS['static']) -> str:
    """ Return path for static object (if it exists) """
    path = os.path.join(path_to_static, filename)

    if os.path.exists(path):
        return path
    elif not filename.endswith(extension):
        LOGGER.debug("Assume file has '%s' extension.", extension)
        path = ".".join((path, extension))

    if not os.path.exists(path):
        LOGGER.error("'%s' isn't exists!", path)
        raise FileNotFoundError(f"'{path}' isn't exists!")

    return path


def load_json(filepath: str, **kwargs) -> dict:
    """ Loads json contents """
    if not os.path.exists(filepath):
        LOGGER.error("File isn't exists '%s'!", filepath)

    with open(filepath, 'r', **kwargs) as fin:
        LOGGER.debug("Loading '%s' content...", filepath)
        return json.load(fin)


def load_plain_text(filepath: str, **kwargs) -> str or list:
    """ Loads plain text file contents as string or list of strings """
    if not os.path.exists(filepath):
        LOGGER.error("File isn't exists '%s'!", filepath)

    with open(filepath, 'r', **kwargs) as fin:
        LOGGER.debug("Loading '%s' content...", filepath)
        return fin.read()
