import os
from typing import NoReturn, Iterable

import yaml


def load_yaml(path: str, **kwargs) -> dict or list:
    if not os.path.exists(path):
        LOGGER.error("Can't find file '%s'", path)
        raise FileNotFoundError(path)

    with open(path, "rb", **kwargs) as fin:
        return yaml.load(fin)


class StaticConfig(object):
    """ Wrapper for static configurations in yaml. """
    DEFAULT_DESTINATION = "output_files"

    @property
    def ok(self) -> bool:
        """ Indicates that configuration has been loaded. """
        return hasattr(self, "v")

    def load(self, path: str, **kwargs) -> object:
        """
            Loads board configuration from static file.

            :param path: absolute path to static file in .yml format.
        """
        LOGGER.debug("Load static config from '%s'", path)

        configs = load_yaml(path, **kwargs)

        self.qpf = configs.get("qpf", {})
        self.qsf = configs.get("qsf", {})
        self.sdc = configs.get("sdc", {})

        v = configs.get("v", {})
        self.v = v.get("assignments", {})
        self.func = v.get("func", {})  # configs for functions

        quartus_version = self.qpf['quartus_version']
        if not self.qsf.get("original_quartus_version"):
            self.qsf['original_quartus_version'] = quartus_version
        if not self.qsf.get("last_quartus_version"):
            self.qsf['last_quartus_version'] = quartus_version

        if not self.qsf.get("project_output_directory"):
            self.qsf['project_output_directory'] = self.DEFAULT_DESTINATION

        return self


class MipsConfig(object):
    """ Wrapper for static configurations for SchoolMIPS. """
    DEFAULT_DESTINATION = "mips"

    def __init__(self, mips_types: Iterable[str]) -> NoReturn:
        self._mips_types = [t.lower() for t in mips_types]

    @property
    def ok(self) -> bool:
        """ Indicates that configuration has been loaded. """
        return hasattr(self, "v")

    @property
    def mips_type(self) -> str or NoReturn:
        if hasattr(self, "mips_type"):
            return self.mips_type

    @mips_type.setter
    def mips_type(self, value: str) -> NoReturn:
        if not isinstance(value, str):
            raise ValueError("Invalid type for SchoolMIPS '%s'", type(value))
        value = value.lower()
        if value not in self._mips_types:
            raise ValueError("Unsupportable SchoolMIPS type '%s'", value)
        self.mips_type = value

    def load(self, path: str, **kwargs) -> object:
        configs = load_yaml(path, **kwargs)
        self.qsf = configs.get("qsf", {})
        self.v = configs.get("v", {})
        return self


class ProjectConfig(object):
    """ Incapsulates project configuration. """

    def __init__(self, *args, **kwargs) -> NoReturn:
        pass
