import os
from typing import NoReturn

from engine.utils.globals import PATHS
from engine.utils.load import Loader
from engine.utils.log import LOGGER
from engine.utils.prepare import Archiver, create_dirs
from engine.utils.render import Render

# all supported boards
BOARDS = ("marsohod2", "marsohod2b", "marsohod3", "marsohod3b")  # "de1soc"


class GenericBoard(object):
    """ Generic board methods (generating configs) """
    DEFAULT_PROJECT_NAME = "generated_project"
    FUNCTIONS = ("ButtonDebouncer", "Demultiplexer",
                 "Generator", "Seven", "Uart8")

    def __init__(self, board_name: str, message: str=None) -> NoReturn:
        """ :param config_path - path to config static file """
        self.board_name = board_name
        self._static_path = '\\'.join((PATHS.STATIC,
                                       ".".join((board_name, "yml"))))
        self.reset()
        self._project_name = self.DEFAULT_PROJECT_NAME
        self.message = message or self._misc.get("message")

    @property
    def project_name(self) -> str:
        return self._project_name

    # BUG: remove
    @project_name.setter
    def project_name(self, value: str) -> NoReturn:
        while isinstance(value, (list, tuple)):
            LOGGER.debug("BUG:\tincorrect project name:\t%s", value)
            value = value[0]
        self._project_name = value or self._project_name

    # NOTE: sdc isn't included, because it generated atomaitcally
    @property
    def params(self) -> dict:
        """ Configurable params """
        # NOTE: 'conf' type is always `int`, 'flt' type is always `bool`
        return {
            'project_name': "Project Name",
            'project_output_directory': "Project Output Folder",
            'message': "Message",
            'flt': tuple(self._qsf['user_assignments'].keys()),
            'func': self.FUNCTIONS,  # type is always `bool`
            'conf': {
                'delay': "Delay",
                'width': "Width",
                'out_freq': "Out Freq",
                'baud_rate': "Baud Rate",
            }  # type is always `int`
        }

    def reset(self, path: str=None) -> object:
        """ Reset board configuration to defaults from static file """
        if not path:
            path = self._static_path
        configs = Loader.load(path)
        self._qpf = configs.get("qpf", {})
        self._qsf = configs.get("qsf", {})
        self._sdc = configs.get("sdc", {})
        self._v = configs.get("v", {}).get("assignments", {})
        self._func = configs.get("v", {}).get("func", {})
        self._misc = configs.get("misc", {})
        self._functions = self.FUNCTIONS

        quartus_version = self._qpf['quartus_version']
        if not self._qsf.get("original_quartus_version"):
            self._qsf['original_quartus_version'] = quartus_version
        if not self._qsf.get("last_quartus_version"):
            self._qsf['last_quartus_version'] = quartus_version
        if not self._qsf.get("project_output_directory"):
            self._qsf['project_output_directory'] = "output_files"
        return self

    def setup(self,
              project_name: str = None,
              flt: dict = None,
              conf: dict = None,
              func: dict = None,
              mips_type: str = None,
              project_output_directory: str = None,
              message: str = None,
              reset: bool = True) -> object:
        """ Setup board configuration """
        flt = flt or {}
        func = func or {}
        self.mips_type = mips_type
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
        self._functions = tuple(f for f in self.FUNCTIONS if func.get(f))
        self.project_name = project_name
        self.message = message or self.message
        self._func.update(conf or {})
        self._qsf['project_output_directory'] = \
            project_output_directory or self._qsf['project_output_directory']
        self._mips_v = {}
        self._mips_qsf = {}
        if self.mips_type:
            if self.board_name.find("marsohod3") > -1:
                mips_configs = Loader.load(PATHS.STATIC + "\\SchoolMips.yml")
                self._mips_qsf = mips_configs.get('qsf', {})
                self._mips_v = mips_configs.get('v', {})
        return self

    def generate(self, project_name: str=None, **kwargs) -> object:
        """ Generates FPGA configs """
        if project_name or kwargs:
            self.setup(project_name=project_name, **kwargs)

        self.configs = {
            'LICENSE': Loader.load_static("LICENSE")
        }

        self.configs.update(dict(zip(
            map(lambda x: ".".join((self.project_name, x)),
                ("v", "qpf", "qsf", "sdc")),
            (Render.v(self.project_name, assignments=self._v,
                      **self._mips_v),
             Render.qpf(self.project_name, **self._qpf),
             Render.qsf(self.project_name, **self._qsf,
                        mips=self._mips_qsf),
             Render.sdc(self.project_name, mips=self.mips_type, **self._sdc))
        )))
        self.configs.update(dict(zip(
            map(lambda x: ".".join((x, "v")), self._functions),
            map(lambda x: Render.functions(".".join((x, "v.jinja")),
                                           **self._func), self._functions)
        )))

        # Generate additional configs for SchoolMIPS
        self.mips_configs = {}
        if self.mips_type:
            self.mips_configs.update({
                'program.hex': Loader.load_static(
                    '\\'.join((PATHS.MIPS, 'program.hex')))
            })
            mips_path = '\\'.join((PATHS.MIPS, self.mips_type, 'src'))
            files = os.listdir(mips_path)
            for file in files:
                self.mips_configs.update({
                    file: Loader.load_static('\\'.join((mips_path, file)))
                })
        return self

    def dump(self, path: str=None) -> object:
        """ Save FPGA config files to separate folder """
        if not path:
            LOGGER.debug("Assume path is project_name='%s'", self.project_name)
            path = self.project_name
        create_dirs(path, rewrite=False)
        for filename, content in self.configs.items():
            with open(os.path.join(path, filename), 'wt') as fout:
                LOGGER.debug("Creating '%s'...", fout.name)
                fout.write(content)

        if self.mips_configs:
            mips_path = path + '\mips'
            create_dirs(mips_path, rewrite=False)
            for filename, content in self.mips_configs.items():
                with open(os.path.join(mips_path, filename), 'wt') as fout:
                    LOGGER.debug("Creating '%s'...", fout.name)
                    fout.write(content)
        return self

    def archive(self, path: str=None, in_memory: bool=False) -> object:
        """ Generate tar file with FPGA config files for specific project """
        if not path and not in_memory:
            LOGGER.debug("Assume path is project_name='%s'", self.project_name)
            path = self.project_name
        if self.mips_configs:
            self.configs.update({'mips': self.mips_configs})
        Archiver.to_tar_flow(self.configs, path=path, in_memory=in_memory)


class Board(GenericBoard):
    """ Predefined board interface """

    def __init__(self, board_name: str) -> NoReturn:
        """ :param board_name - name of existing board """
        board_name = board_name.lower()
        if board_name not in BOARDS:
            LOGGER.error("Incorrect board name: %s", board_name)
            raise ValueError(f"Incorrect board name: {board_name}")
        super(Board, self).__init__(board_name)
