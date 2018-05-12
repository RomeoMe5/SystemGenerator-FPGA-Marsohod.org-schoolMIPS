import os

from engine.utils.load import Loader
from engine.utils.log import LOGGER
from engine.utils.prepare import Archiver, create_dirs
from engine.utils.render import Render

LICENSE = Loader.load_static("LICENSE").decode("utf-8")


class GenericBoard(object):
    """ Generic board methods (generating configs) """
    DEFAULT_PROJECT_NAME = "generated_project"

    def __init__(self, config_name: str=None, config_path: str=None) -> None:
        """ :param config_name - instance to load from static files. """
        self.message = "THIS CLASS SHOULD BE USED ONLY BY ADVANCED USERS!"
        if config_name is not None:
            self._filename = config_name
            self._static = Loader.load_static(self._filename)
        elif config_path is not None:
            self._filename = config_path
            self._static = Loader.load(self._filename)
        else:
            self._filename = "[manual]"
            LOGGER.warning("Static content should be loaded manually!")
        self._project_name = GenericBoard.DEFAULT_PROJECT_NAME
        self._configs = None

    @staticmethod
    def _generate(project_name: str, **configs) -> dict:
        """ Generates FPGA configs """
        return {
            'v': Render.v(project_name, **configs.get('v', {})),
            'qpf': Render.qpf(project_name, **configs.get('qpf', {})),
            'qsf': Render.qsf(project_name, **configs.get('qsf', {})),
            'sdc': Render.sdc(project_name, **configs.get('sdc', {}))
        }

    @staticmethod
    def _archive(path: str, **configs) -> None:
        """ Generate tar file with FPGA config files """
        project_name = os.path.split(path)[-1]
        config_files = {}
        for extension, content in configs.items():
            filename = ".".join((project_name, extension))
            config_files[filename] = content
            LOGGER.debug("Adding '%s'", filename)
        config_files['LICENSE'] = LICENSE
        LOGGER.debug("Adding LICENSE")
        Archiver.to_tar_flow(config_files, path)

    @staticmethod
    def _save_to_file(path: str, filename: str, content: object) -> None:
        """ Save content to file """
        with open(os.path.join(path, filename), 'wt') as fout:
            LOGGER.info("Creating '%s'...", fout.name)
            fout.write(content)

    @staticmethod
    def _dump(path: str, **configs) -> None:
        """ Save FPGA config files to separate folder. """
        project_name = os.path.split(path)[-1]
        create_dirs(path, rewrite=False)
        for extension, content in configs.items():
            filename = ".".join((project_name, extension))
            GenericBoard._save_to_file(path, filename, content)
        GenericBoard._save_to_file(path, "LICENSE", LICENSE)

    @staticmethod
    def _filter_none(**config) -> dict:
        """ Remove missed values from configuration. """
        for key in set(config).copy():
            value = config[key]
            if isinstance(value, dict):
                config[key] = GenericBoard._filter_none(**value)
            elif value is None:
                del config[key]
        return config

    @property
    def configs(self) -> dict:
        if self._configs is None:
            self._configs = GenericBoard._generate(self._project_name,
                                                   **self._static)
        return self._configs

    def generate(self, project_name: str, **kwargs) -> object:
        """ Generates FPGA configs for specific project """
        self._project_name = project_name
        self._configs = GenericBoard._generate(project_name, **self._static)
        return self

    def archive(self,
                project_name: str=None,
                project_path: str=None,
                force: bool=False,
                **kwargs) -> object:
        """ Generate tar file with FPGA config files for specific project """
        if self._configs is None or force:
            assert project_name
            self.generate(project_name, **kwargs)

        if not project_path:
            project_path = self._project_name

        self._archive(project_path, **self._configs)
        return self

    def dump(self, path: str=None) -> object:
        """ Save FPGA config files to separate folder. """
        if not path:
            path = self._project_name
        GenericBoard._dump(path, **self._configs)
        return self

    def generate_files(self,
                       project_name: str=None,
                       project_path: str=None,
                       force: bool=False,
                       **kwargs) -> object:
        """
           Generates FPGA config files for specific project in separate folder.

            :param project_path :type str - specific path to the project
                (default=project_name)
            :param force :type bool - force config to be recreated
        """
        if self._configs is None or force:
            assert project_name
            return self.generate(project_name, **kwargs).dump(project_path)
        return self.dump(project_path)

    def __repr__(self) -> str:
        base = f"<{self.__class__.__name__}::{hex(id(self))}>"
        if self._configs is None:
            return base
        return base + f"{str(self._configs)[:50]}..." + "}"
