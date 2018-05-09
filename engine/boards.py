import os

from engine.utils import PATHS
from engine.utils.load import Loader
from engine.utils.log import LOGGER, log
from engine.utils.prepare import Archiver, create_dirs
from engine.utils.render import Render

LICENSE = Loader.load_static("LICENSE")


class GenericBoard(object):
    """ Generic board methods (generating configs) """

    @log
    def __init__(self, config_name: str) -> None:
        self._filename = config_name
        self.config = Loader.load_static(self._filename)

    @log
    def generate(self, project_name: str, **kwargs) -> dict:
        """ Returns FPGA configs """
        return {
            'v': Render.v(
                project_name=project_name,
                **self.config.get('v', {})
            ),
            'qpf': Render.qpf(
                project_name=project_name,
                **self.config.get('qpf', {})
            ),
            'qsf': Render.qsf(
                project_name=project_name,
                **self.config.get('qsf', {})
            ),
            'sdc': Render.sdc(
                project_name=project_name,
                **self.config.get('sdc', {})
            )
        }

    def generate_archive(self, project_name: str, **kwargs) -> object:
        """ Generate tar file with FPGA config files """
        config_files_extensions = self.generate(project_name, **kwargs)
        config_files = {}

        for extension, content in config_files_extensions.items():
            filename = ".".join((project_name, extension))
            config_files[filename] = content
            LOGGER.debug("  Adding '%s': ''%s ", filename, content)
        config_files['LICENSE'] = LICENSE
        LOGGER.debug("  Adding LICENSE : '%s'", LICENSE)
        Archiver.to_tar_flow(config_files, project_name)
        return self

    def generate_files(self, project_name: str, **kwargs) -> object:
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
            GenericBoard._save_to_file(project_path, filename, content)

        return self

    @staticmethod
    def _save_to_file(path: str, filename: str, content: object) -> None:
        """ Save content to file """
        with open(os.path.join(path, filename), 'wt') as fout:
            LOGGER.info("Creating '%s'...", fout.name)
            fout.write(content)


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


# TODO: remove this class, it exists only for debug
class DE1SoC(GenericBoard):
    """
        DE1SoC configs generator (for debug only)

        Use official Altera system builder for this type of boards.
    """

    def __init__(self) -> None:
        super(DE1SoC, self).__init__(self.__class__.__name__)
