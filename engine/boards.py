import io
import logging
import os
from collections import namedtuple
from functools import reduce
from typing import Any, NoReturn, Tuple

from engine.constants import (BOARDS, DEFAULT_PROJECT_NAME, DESTINATIONS,
                              FUNCTIONS, MIPS, PATHS)
from engine.exceptions import InvalidProjectName
from engine.utils.prepare import (Archiver, Loader, create_dirs,
                                  validate_project_name)
from engine.utils.render import Render


class GenericBoard(object):
    """ Generic board methods (generating configs) """

    __slots__ = (
        "configs",
        "_static_path",
        "_qsf",
        "_mips_qsf",
        "_qpf",
        "_v",
        "_sdc",
        "_func",
        "_mips_type",
        "_project_name",
        "_mips_v",
        "mips_configs",
        "_functions"
    )

    def __init__(self, config_path: str) -> NoReturn:
        """ :param config_path - full path to config static file """
        self.config_path = config_path
        self.project_name = DEFAULT_PROJECT_NAME

    @property
    def config_path(self) -> str:
        return self._static_path

    @config_path.setter
    def config_path(self, value: str) -> NoReturn:
        logging.debug("Setup board config path: %s", value)
        if not os.path.exists(value):
            raise FileNotFoundError("Config path not exists: {}".format(value))
        self._static_path = value
        self.reset()  # read config to local variables for convenience

    @staticmethod
    def func_path(func_name: str) -> str:
        return DESTINATIONS.FUNC + "/" + func_name

    @property
    def project_name(self) -> str:
        return self._project_name

    # BUG with passing params, should be removed
    @project_name.setter
    def project_name(self, value: str) -> NoReturn:
        while isinstance(value, (list, tuple)):
            logging.warning("BUG:\tincorrect project name:\t%s", value)
            value = value[0]
        self._project_name = value or DEFAULT_PROJECT_NAME
        if not validate_project_name(self._project_name):
            raise InvalidProjectName(self.project_name)

    # NOTE sdc isn't included, because it is generated atomaitcally
    @property
    def params(self) -> dict:
        """ Configurable params """
        return self._qsf['user_assignments']

    @property
    def as_archive(self) -> io.BytesIO:
        """ Returns generated configs as archive. """
        return Archiver.get_tar_io(self.configs)

    def reset(self, path: str = None, mips_type: str = None) -> object:
        """
            Reloads board configuration from static file

            :param path: absolute path to static file.
                Uses from default file if None.
            :param mips_type: version of SchoolMIPS core.
                Mips won't be added in project if None
        """
        configs = Loader.load(path or self._static_path)

        self._qpf = configs.get("qpf", {})
        self._qsf = configs.get("qsf", {})
        self._sdc = configs.get("sdc", {})
        v = configs.get("v", {})
        self._v = v.get("assignments", {})
        self._func = v.get("func", {})
        self._functions = tuple(self.func_path(f)
                                for f in FUNCTIONS.ITEMS.keys())

        self._reset_mips(Loader.get_static_path(MIPS.CONFIG), mips_type)

        quartus_version = self._qpf['quartus_version']
        if not self._qsf.get("original_quartus_version"):
            self._qsf['original_quartus_version'] = quartus_version
        if not self._qsf.get("last_quartus_version"):
            self._qsf['last_quartus_version'] = quartus_version
        if not self._qsf.get("project_output_directory"):
            self._qsf['project_output_directory'] = DESTINATIONS.OUTPUT
        return self

    def _reset_mips(self, config_path: str, mips_type: str) -> NoReturn:
        self._mips_qsf = {}
        self._mips_v = {}
        if mips_type and mips_type not in MIPS.VERSIONS:
            logging.error("Unsupportable mips type: %s", mips_type)
            mips_type = None
        if mips_type:
            mips_configs = Loader.load(config_path)
            self._mips_qsf = mips_configs.get("qsf", {})
            self._mips_v = mips_configs.get("v", {})
        self._mips_type = mips_type

    def setup(self,
              project_name: str = None,
              flt: dict = None,
              conf: dict = None,
              func: dict = None,
              mips_type: str = None,
              project_output_directory: str = None,
              reset: bool = True) -> object:
        """
            Setup board configuration

            :param flt: filters for configurations
            :param conf: additional configurations for fuctions
            :param func: list of functions to include in project
            :param mips_type: version of SchoolMIPS core.
                Mips won't be added in project if None
            :param reset: whether to reload configurations from file
        """
        flt = flt or {}
        func = func or {}
        if reset:
            self.reset(mips_type=mips_type)

        def _filter(params: dict) -> dict:
            for key in set(params).copy():
                if not flt.get(key) and not flt.get(key.lower()):
                    del params[key]
            return params

        self.project_name = project_name
        self._qsf['user_assignments'] = _filter(self._qsf['user_assignments'])
        self._v = _filter(self._v)

        self._functions = tuple(self.func_path(f)
                                for f in FUNCTIONS.ITEMS.keys() if func.get(f))
        self._func.update(conf or {})
        self._qsf['project_output_directory'] = \
            project_output_directory or self._qsf['project_output_directory']
        return self

    def generate(self, project_name: str = None, **kwargs) -> object:
        """ Generates FPGA configs """
        if project_name or kwargs:
            self.setup(project_name=project_name, **kwargs)

        self.configs = {'LICENSE': Loader.load_static("LICENSE")}

        self.configs.update(dict(zip(
            map(lambda x: f"{self.project_name}.{x}",
                ("v", "qpf", "qsf", "sdc")),
            (Render.v(self.project_name, assignments=self._v, **self._mips_v),
             Render.qpf(self.project_name, **self._qpf),
             Render.qsf(self.project_name, func=self._functions,
                        mips=self._mips_qsf, **self._qsf),
             Render.sdc(self.project_name, mips=self._mips_type, **self._sdc))
        )))

        # NOTE additional modules are placed in separate folder 'functions'
        self.configs.update(dict(zip(
            map(lambda x: x + ".v", self._functions),  # file paths
            map(lambda x: Render.functions(x, **self._func), self._functions)
        )))

        if self._mips_type:
            # Generate additional configs for SchoolMIPS
            program_hex = os.path.join(PATHS.MIPS, "program.hex")
            self.configs['program.hex'] = Loader.load_static(program_hex)
            mips_path = os.path.join(PATHS.MIPS, self._mips_type)
            files = os.listdir(mips_path)
            self.configs.update(dict(zip(
                map(lambda x: os.path.join(DESTINATIONS.MIPS, x), files),
                map(lambda x: Loader.load_static(x, mips_path), files)
            )))
        return self

    def dump(self, path: str = None) -> object:
        """ Save FPGA config files to separate folder """
        path = path or self.project_name
        create_dirs(path, rewrite=False)

        if self._functions:
            create_dirs(os.path.join(path, DESTINATIONS.FUNC))
        if self._mips_type:
            create_dirs(os.path.join(path, DESTINATIONS.MIPS))

        def save_to_file(filename: str, content: Any) -> NoReturn:
            logging.debug("Creating '%s'...", os.path.join(path, filename))
            try:
                with open(os.path.join(path, filename), "w") as fout:
                    fout.write(content)
            except BaseException as exc:
                logging.info("Can't create '%s' due to:\n%s", filename, exc)
                return True
            return False

        errors_count = reduce(
            lambda x, y: x + y,
            map(lambda x: save_to_file(*x), self.configs.items())
        )
        if errors_count:
            logging.warning("%d errors count while dumping to '%s'",
                            errors_count, path)
        return self

    def archive(self, path: str = None) -> object:
        """ Generate tar file with FPGA config files for specific project """
        Archiver.to_tar_flow(self.configs, path=path or self.project_name)
        return self


class Board(GenericBoard):
    """ Predefined board interface """

    __slots__ = GenericBoard.__slots__

    def __init__(self, board_name: str) -> NoReturn:
        """ :param board_name - name of existing board """
        board_name = board_name.lower()

        if board_name not in BOARDS:
            logging.error("Incorrect board name: %s", board_name)
            raise ValueError("Incorrect board name: {}".format(board_name))

        super(Board, self).__init__(Loader.get_static_path(board_name))
