# [future] TODO add __slots__ to optimize memory usage

import io
import os
from collections import namedtuple
from functools import reduce
from typing import Any, NoReturn, Tuple

from engine.utils.globals import LOGGER, PATHS
from engine.utils.prepare import Archiver, Loader, create_dirs
from engine.utils.render import Render


# native supported boards
BOARDS = ("marsohod2", "marsohod2b", "marsohod3", "marsohod3b")  # "de1soc"


class GenericBoard(object):
    """ Generic board methods (generating configs) """

    __slots__ = ("_static_path", "_project_name", "message", "_func", "_misc",
                 "_qpf", "_qsf", "_sdc", "_v", "_functions", "configs",
                 "_mips_qsf", "_mips_v", "_mips_type", "mips_configs")

    MIPS_CONFIG = "SchoolMips.yml"
    FUNC_DIR = "functions"
    MIPS_DIR = "mips"
    MIPS_TYPES = ("simple", "mmio", "irq", "pipeline", "pipeline_irq",
                  "pipeline_ahb")
    FUNCTIONS = {
        'ButtonDebouncer': "Button Debouncer: add delay between button inputs",
        'Demultiplexer': "Simple Demultiplexer",
        'Generator': "Frequency Generator: decrease internal board clock rate",
        'Seven': "7-segment indicator controller",
        'Uart8': "Simple 8-bit UART"
    }
    Param = namedtuple("Param", ("items", "type"))

    def __init__(self, config_path: str, message: str=None) -> NoReturn:
        """ :param config_path - full path to config static file """
        self._static_path = {}
        self.config_path = config_path
        self._project_name = "my-project"  # default project name
        self.message = message or self._misc.get("message")

    @property
    def config_path(self) -> str:
        return self._static_path

    @config_path.setter
    def config_path(self, value: str) -> NoReturn:
        if not os.path.exists(value):
            raise FileNotFoundError("Config path not exists: {}".format(value))
        self._static_path = value
        self.reset()  # read config to local variables for convenience

    @property
    def FUNCS(_) -> Tuple[str]:
        return tuple(GenericBoard.FUNCTIONS.keys())

    def func_path(self, func_name: str) -> str:
        return self.FUNC_DIR + "/" + func_name

    @property
    def project_name(self) -> str:
        return self._project_name

    # [dev] BUG with passing params, should be removed
    @project_name.setter
    def project_name(self, value: str) -> NoReturn:
        while isinstance(value, (list, tuple)):
            LOGGER.warning("BUG:\tincorrect project name:\t%s", value)
            value = value[0]
        self._project_name = value or self._project_name

    # NOTE sdc isn't included, because it generated atomaitcally
    @property
    def params(self) -> dict:
        """ Configurable params """
        return {
            'project_name': self.Param("Project Name", str),
            'project_output_directory': self.Param("Project Output Dir", str),
            'message': self.Param("Additional Message", str),
            'flt': self.Param(tuple(self._qsf['user_assignments'].keys()),
                              bool),
            'func': self.Param(GenericBoard.FUNCTIONS, bool),
            'conf': self.Param({
                'delay': "Delay",
                'width': "Input Width",
                'out_freq': "Output Frequency",
                'baud_rate': "Board Baud Rate",
            }, int)  # configurations for functions
        }

    @property
    def as_archive(self) -> io.BytesIO:
        return Archiver.get_tar_io(self.configs)

    def reset(self, path: str=None) -> object:
        """ Reset board configuration to defaults from static file """
        configs = Loader.load(path or self._static_path)
        self._qpf = configs.get("qpf", {})
        self._qsf = configs.get("qsf", {})
        self._sdc = configs.get("sdc", {})
        v = configs.get("v", {})
        self._v = v.get("assignments", {})
        self._func = v.get("func", {})
        self._misc = configs.get("misc", {})
        self._functions = tuple(self.func_path(f) for f in self.FUNCS)

        self.mips_configs = {}
        self._mips_type = None
        mips_configs = Loader.load(
            Loader.get_static_path(self.MIPS_CONFIG)
        )
        self._mips_qsf = mips_configs.get("qsf", {})
        self._mips_v = mips_configs.get("v", {})

        quartus_version = self._qpf['quartus_version']
        if not self._qsf.get("original_quartus_version"):
            self._qsf['original_quartus_version'] = quartus_version
        if not self._qsf.get("last_quartus_version"):
            self._qsf['last_quartus_version'] = quartus_version
        if not self._qsf.get("project_output_directory"):
            self._qsf['project_output_directory'] = "output_files"
        return self

    def setup(self,
              project_name: str=None,
              flt: dict=None,
              conf: dict=None,
              func: dict=None,
              mips_type: str=None,
              project_output_directory: str=None,
              message: str=None,
              reset: bool=True) -> object:
        """ Setup board configuration """
        flt = flt or {}
        func = func or {}
        if mips_type and mips_type not in self.MIPS_TYPES:
            LOGGER.error("Unsupportable mips type: %s", mips_type)
            mips_type = None
        self._mips_type = mips_type
        if reset:
            self.reset()

        def _filter(params: dict) -> dict:
            for key in set(params).copy():
                if not flt.get(key.lower()):
                    del params[key]
            return params

        self._qsf['user_assignments'] = _filter(
            self._qsf['user_assignments'])
        self._v = _filter(self._v)

        self._functions = tuple(self.func_path(f)
                                for f in self.FUNCS if func.get(f))
        self.project_name = project_name or self.project_name
        self.message = message or self.message
        self._func.update(conf or {})
        self._qsf['project_output_directory'] = \
            project_output_directory or self._qsf['project_output_directory']
        return self

    def generate(self, project_name: str=None, **kwargs) -> object:
        """ Generates FPGA configs """
        if project_name or kwargs:
            self.setup(project_name=project_name, **kwargs)

        self.configs = {
            'LICENSE': Loader.load_static("LICENSE", encoding="utf-8")
        }

        self.configs.update(dict(zip(
            map(lambda x: self.project_name + "." + x,
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
            self.mips_configs = {
                'program.hex': Loader.load_static(os.path.join(PATHS.MIPS,
                                                               "program.hex"))
            }
            mips_path = os.path.join(PATHS.MIPS, self._mips_type, "src")
            files = os.listdir(mips_path)
            self.mips_configs.update(dict(zip(
                map(lambda x: os.path.join(self.MIPS_DIR, x), files),
                map(lambda x: Loader.load_static(x, mips_path), files)
            )))
        return self

    def dump(self, path: str=None) -> object:
        """ Save FPGA config files to separate folder """
        path = path or self.project_name
        create_dirs(path, rewrite=False)

        if self._functions:
            create_dirs(os.path.join(path, self.FUNC_DIR))
        if hasattr(self, "mips_configs") and self.mips_configs:
            create_dirs(os.path.join(path, self.MIPS_DIR))

        def save_to_file(filename: str, content: Any) -> NoReturn:
            LOGGER.debug("Creating '%s'...", os.path.join(path, filename))
            try:
                with open(os.path.join(path, filename), "w") as fout:
                    fout.write(content)
            except BaseException as exc:
                LOGGER.info("Can't create '%s' due to:\n%s", filename, exc)
                return False
            return True

        errors_count = reduce(lambda x, y: x + y, map(
            lambda x: save_to_file(*x),
            list(self.configs.items()) + list(self.mips_configs.items())
        ))
        if errors_count:
            LOGGER.warning("%d errors count while dumping to '%s'",
                           errors_count, path)
        return self

    def archive(self, path: str=None) -> object:
        """ Generate tar file with FPGA config files for specific project """
        if hasattr(self, "mips_configs") and self.mips_configs:
            self.configs.update({'mips': self.mips_configs})
        Archiver.to_tar_flow(self.configs, path=path or self.project_name)
        return self


class Board(GenericBoard):
    """ Predefined board interface """

    __slots__ = GenericBoard.__slots__

    def __init__(self, board_name: str) -> NoReturn:
        """ :param board_name - name of existing board """
        board_name = board_name.lower()
        if board_name not in BOARDS:
            LOGGER.error("Incorrect board name: %s", board_name)
            raise ValueError("Incorrect board name: {}".format(board_name))
        super(Board, self).__init__(Loader.get_static_path(board_name))
