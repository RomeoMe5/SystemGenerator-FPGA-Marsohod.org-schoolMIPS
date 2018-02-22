import logging
import os

from engine.utils.load import get_static_path, load_json, load_plain_text
from engine.utils.prepare import create_dirs, Archiver
from engine.utils.render import Render

try:
    from configs.engine import CONFIG
except ImportError as err:
    logging.warning("Can't import configuration!\n%s", err)
    from engine.utils import Config as CONFIG

LICENSE = load_plain_text(os.path.join(CONFIG.PATHS['static'], "LICENSE"))


class GenericBoard(object):
    """ Generic board functionality """

    def __init__(self, config_name: str) -> None:
        self._path = get_static_path(config_name)
        self.config = load_json(
            os.path.join(CONFIG.PATHS['static'], self._path)
        )

    def generate(self,
                 project_name: str,
                 **kwargs) -> dict:
        """ Returns FPGA configs """
        return {
            'v': Render.v(project_name=project_name, **kwargs),
            'qpf': Render.qpf(**kwargs),
            'qsf': Render.qsf(**kwargs),
            'sdc': Render.sdc(**kwargs)
        }

    def generate_archive(self,
                         project_name: str,
                         **kwargs) -> None:
        config_files_extensions = self.generate(project_name, **kwargs)
        config_files = dict()
        for extension, content in config_files_extensions.items():
            filename = ".".join((project_name, extension))
            config_files.update({filename: content})

        Archiver.to_tar_flow(config_files, project_name)

    def generate_files(self,
                       project_name: str,
                       **kwargs) -> None:
        """
            Generates FPGA config files

            :param path :type str - separate name for project folder
                (default == project_name)
        """
        config_files = self.generate(project_name, **kwargs)
        project_path = kwargs.pop('path', project_name)
        create_dirs(project_path, rewrite=False)

        for extension, content in config_files.items():
            filename = ".".join((project_name, extension))
            with open(os.path.join(project_path, filename), 'wt') as fout:
                logging.info("Creating '%s'...", fout.name)
                fout.write(content)

        if kwargs.pop('add_license', True):
            GenericBoard.save_license_file(project_path)

    @staticmethod
    def save_license_file(path: str) -> None:
        """ Save License file to certain folder """
        with open(os.path.join(path, "LICENSE"), 'wt') as fout:
            logging.debug("Adding LICENSE: '%s'.", fout.name)
            fout.write(LICENSE)


class Marsohod2(GenericBoard):
    """TODO: add description"""

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)


class Marsohod2B(GenericBoard):
    """TODO: add description"""

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)


class Marsohod3(GenericBoard):
    """TODO: add description"""

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)


class Marsohod3B(GenericBoard):
    """TODO: add description"""

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)
