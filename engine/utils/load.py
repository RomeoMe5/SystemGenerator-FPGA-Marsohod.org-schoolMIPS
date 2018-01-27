import logging
import os

from engine.utils import PATHS


def get_static_path(filename: str,
                    extension: str="json",
                    path_to_static: str=PATHS['static']) -> str:
    """  """
    path = os.path.join(path_to_static, filename)

    if extension:
        path = ".".join((path, extension))

    if not os.path.exists(path):
        logging.error("'%s' isn't exists!", path)
        raise FileNotFoundError(f"'{path}' isn't exists!")

    return path
