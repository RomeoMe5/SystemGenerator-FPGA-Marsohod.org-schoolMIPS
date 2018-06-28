import os
from typing import Any

from engine.utils.globals import PATHS, SUPPORTED_EXTENSIONS, SUPPORTED_LOADERS
from engine.utils.log import LOGGER


class Loader(object):
    """ Implements file content loading """

    @staticmethod
    def load(filepath: str,
             loader_params: dict=None,
             **kwargs) -> Any:
        """ Loads content of static file from any location """
        file_format = filepath.split('.')[-1].lower()
        loader_params = loader_params or {}
        with open(filepath, 'rb', **kwargs) as fin:
            LOGGER.debug("Loading '%s' content...", filepath)
            for extension in SUPPORTED_EXTENSIONS:
                if file_format == extension:
                    return SUPPORTED_LOADERS[extension](fin, **loader_params)
            return fin.read()  # read plain text

    @staticmethod
    def load_static(filename: str,
                    path_to_static: str=PATHS.STATIC,
                    loader_params: dict=None,
                    **kwargs) -> Any:
        """ Loads content of static file from engine 'static' folder """
        filepath = Loader.get_static_path(filename, path_to_static)
        return Loader.load(filepath, loader_params, **kwargs)

    @staticmethod
    def get_static_path(filename: str,
                        path_to_static: str=PATHS.STATIC) -> str:
        """ Return path for static object (if it exists) """
        path = os.path.join(path_to_static, filename)

        if os.path.exists(path):
            return path

        for extension in SUPPORTED_EXTENSIONS:
            if not filename.endswith(extension):
                LOGGER.debug("Assume file has '%s' extension.", extension)
                path = ".".join((path, extension))
                if os.path.exists(path):
                    return path

        LOGGER.error("'%s' isn't exists!", path)
        raise FileNotFoundError(f"'{path}' isn't exists!")
