# [future] TODO add __slots__ to optimize memory usage

import asyncio
import io
import os
from collections import namedtuple
from typing import Any, NoReturn, Tuple

from engine.utils.globals import LOGGER, PATHS
from engine.utils.misc import get_event_loop
from engine.utils.prepare import Archiver, Loader, create_dirs
from engine.utils.render import Render


# all supported boards
BOARDS = ("marsohod2", "marsohod2b", "marsohod3", "marsohod3b")  # "de1soc"


class GenericBoard(object):
    """ Generic board methods (generating configs) """
    __slots__ = ("_static_path", "_project_name", "message", "_func", "_misc",
                 "_qpf", "_qsf", "_sdc", "_v", "_functions", "configs")

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
        self._static_path = config_path
        self.reset()  # read config to local variables for convenience
        self._project_name = "my-project"  # default project name
        self.message = message or self._misc.get("message")

    @property
    def FUNCS(_) -> Tuple[str]:
        return tuple(GenericBoard.FUNCTIONS.keys())

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
        return asyncio.run(Archiver.get_tar_io(self.configs))

    def reset(self, path: str=None) -> object:
        """ Reset board configuration to defaults from static file """
        configs = asyncio.run(Loader.load(path or self._static_path))
        self._qpf = configs.get("qpf", {})
        self._qsf = configs.get("qsf", {})
        self._sdc = configs.get("sdc", {})
        v = configs.get("v", {})
        self._v = v.get("assigments", {})
        self._func = v.get("func", {})
        self._misc = configs.get("misc", {})
        self._functions = self.FUNCS

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
              project_output_directory: str=None,
              message: str=None,
              reset: bool=True) -> object:
        """ Setup board configuration """
        flt = flt or {}
        func = func or {}
        if reset:
            self.reset()

        def _filter(params: dict) -> dict:
            for key in set(params).copy():
                if not flt.get(key.lower()):
                    del params[key]
            return params

        self._qsf['user_assignments'] = _filter(self._qsf['user_assignments'])
        self._v = _filter(self._v)

        self._functions = tuple(f for f in self.FUNCS if func.get(f))
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
            'LICENSE': asyncio.run(Loader.load_static("LICENSE",
                                                      encoding="utf-8"))
        }

        tasks = (Render.v(self.project_name, assigments=self._v),
                 Render.qpf(self.project_name, **self._qpf),
                 Render.qsf(self.project_name, **self._qsf),
                 Render.sdc(self.project_name, **self._sdc))
        with get_event_loop() as loop:
            self.configs.update(dict(zip(
                map(lambda x: ".".join((self.project_name, x)),
                    ("v", "qpf", "qsf", "sdc")),
                loop.run_until_complete(asyncio.gather(*tasks))
            )))

        tasks = map(lambda x: Render.functions(x, **self._func),
                    self._functions)
        with get_event_loop() as loop:
            self.configs.update(dict(zip(
                map(lambda x: ".".join((x, "v")), self._functions),
                loop.run_until_complete(asyncio.gather(*tasks))
            )))

        return self

    def dump(self, path: str=None) -> object:
        """ Save FPGA config files to separate folder """
        create_dirs(path or self.project_name, rewrite=False)

        async def save_to_file(filename: str, content: Any) -> NoReturn:
            with open(os.path.join(path, filename), "w") as fout:
                LOGGER.debug("Creating '%s'...", fout.name)
                fout.write(content)

        tasks = (save_to_file(filename, content)
                 for filename, content in self.configs.items())
        with get_event_loop() as loop:
            loop.run_until_complete(asyncio.gather(*tasks))
        return self

    def archive(self, path: str=None) -> object:
        """ Generate tar file with FPGA config files for specific project """
        asyncio.run(Archiver.to_tar_flow(self.configs,
                                         path=path or self.project_name))
        return self


class Board(GenericBoard):
    """ Predefined board interface """

    __slots__ = GenericBoard.__slots__

    def __init__(self, board_name: str) -> NoReturn:
        """ :param board_name - name of existing board """
        board_name = board_name.lower()
        if board_name not in BOARDS:
            LOGGER.error("Incorrect board name: %s", board_name)
            raise ValueError(f"Incorrect board name: {board_name}")
        super(Board, self).__init__(
            asyncio.run(Loader.get_static_path(board_name))
        )
