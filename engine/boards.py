import os

from engine.utils import PATHS
from engine.utils.load import get_static_path, load_json, load_plain_text
from engine.utils.log import LOGGER, log
from engine.utils.prepare import Archiver, create_dirs
from engine.utils.render import Render

LICENSE = load_plain_text(os.path.join(PATHS['static'], "LICENSE"))


class GenericBoard(object):
    """ Generic board methods (generating configs) """

    @log
    def __init__(self, config_name: str) -> None:
        self._path = get_static_path(config_name)
        self.config = load_json(
            os.path.join(PATHS['static'], self._path)
        )

    @log
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

    # TODO: ad logging
    def generate_archive(self, project_name: str, **kwargs) -> None:
        """ Generate tar file with FPGA config files """
        config_files_extensions = self.generate(project_name, **kwargs)
        config_files = dict()
        LOGGER.debug("Create new dictionary(config_files)")
        for extension, content in config_files_extensions.items():
            filename = ".".join((project_name, extension))
            config_files.update({filename: content})
            LOGGER.debug("  Adding '%s': ''%s ", filename, content)
        config_files.update({"LICENSE": LICENSE})
        LOGGER.debug("  Adding LICENSE : '%s'", LICENSE)
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
                LOGGER.info("Creating '%s'...", fout.name)
                fout.write(content)

        with open(os.path.join(project_path, "LICENSE"), 'wt') as fout:
            LOGGER.debug("Adding LICENSE: '%s'.", fout.name)
            fout.write(LICENSE)


class Marsohod2(GenericBoard):
    """ Marsohod2 configs generator """

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)


class Marsohod2B(GenericBoard):
    """ Marsohod2Bis configs generator """

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)


class Marsohod3(GenericBoard):
    """ Marsohod3 configs generator """

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)


class Marsohod3B(GenericBoard):
    """ Marsohod3Bis configs generator """

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)
