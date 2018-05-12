import os

from engine.utils import PATHS
from engine.utils.load import Loader
from engine.utils.log import LOGGER, log
from engine.utils.prepare import Archiver, create_dirs
from engine.utils.render import Render

LICENSE = Loader.load_static("LICENSE").decode("utf-8")


# [urgent] [feature] TODO: add filtering
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
        for key in config:
            value = config[key]
            if isinstance(value, dict):
                config[key] = GenericBoard._filter_none(value)
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


class ManualBoard(object):
    """ Boart which accepts manual configuration files """

    def __init__(self, config_path: str=None, static: dict=None) -> None:
        if config_path is not None:
            super(ManualBoard, self).__init__(config_path)
        else:
            assert isinstance(static, dict)
            super(ManualBoard, self).__init__()
            self._static = static
        self.message = None


class Marsohod2(GenericBoard):
    """ Marsohod2 configs generator """

    def __init__(self) -> None:
        super(Marsohod2, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS IS UNDER DEVELOPMENT: NO WARRANTY PROVIDED!"
        LOGGER.warning(self.message)


class Marsohod2B(GenericBoard):
    """ Marsohod2Bis configs generator """

    def __init__(self) -> None:
        super(Marsohod2B, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS IS UNDER DEVELOPMENT: NO WARRANTY PROVIDED!"
        LOGGER.warning(self.message)


class Marsohod3(GenericBoard):
    """ Marsohod3 configs generator """

    def __init__(self) -> None:
        super(Marsohod3, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS IS UNDER DEVELOPMENT: NO WARRANTY PROVIDED!"
        LOGGER.warning(self.message)


class Marsohod3B(GenericBoard):
    """ Marsohod3Bis configs generator """

    def __init__(self) -> None:
        super(Marsohod3B, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS IS UNDER DEVELOPMENT: NO WARRANTY PROVIDED!"
        LOGGER.warning(self.message)


# [minor] [dev] TODO: remove this class, it exists only for debug
class DE1SoC(GenericBoard):
    """
        DE1SoC configs generator (for debug only)

        Use official Altera system builder for this type of boards.
    """

    def __init__(self) -> None:
        super(DE1SoC, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS SHOULD BE USED ONLY FOR DEBUGGING.\n"
            "Please, use the oficial Altera app for generating "
            "configs for this type of devices."
        LOGGER.warning(self.message)

    # [feature] TODO: add support for correct filtering .sdc-files
    def generate(self,
                 project_name: str,
                 # qpf: optional
                 quartus_version: str="15.1.0",
                 # qsf: optional
                 original_quartus_version: str=None,  # default=quartus_version
                 last_quartus_version: str=None,  # default=quartus_version
                 # qsf-v
                 audio: bool=False,
                 clock: bool=False,
                 i2c_for_audio_and_video_in: bool=False,
                 key: bool=False,
                 # v
                 adc: bool=False,
                 sdram: bool=False,
                 seg7: bool=False,
                 ir: bool=False,
                 led: bool=False,
                 ps2: bool=False,
                 sw: bool=False,
                 video_in: bool=False,
                 vga: bool=False,
                 hps: bool=False,
                 # sdc - currently not supported
                 create_clock: bool=False,
                 create_generated_clock: bool=False,
                 set_clock_latency: bool=False,
                 set_clock_uncertainty: bool=False,
                 set_input_delay: bool=False,
                 set_output_delay: bool=False,
                 set_clock_groups: bool=False,
                 set_false_path: bool=False,
                 set_multicycle_path: bool=False,
                 set_maximum_delay: bool=False,
                 set_minimum_delay: bool=False,
                 set_load: bool=False) -> object:
        """ Generates FPGA configs for specific project """
        qsf = self._static['qsf']
        global_assignments = qsf['global_assignments']
        user_assignments = qsf['user_assignments']
        qpf = self._static['qpf']
        sdc = self._static['sdc']
        v = self._static['v']['assigments']  # warning: may be changed

        self.__filtered_static = self._filter_none(**{
            'v': {
                'ADC': v['ADC'] if adc else None,
                'Audio': v['Audio'] if audio else None,
                'Clock': v['Clock'] if clock else None,
                'SDRAM': v['SDRAM'] if sdram else None,
                'I2C for Audio and Video-In': v[
                    'I2C for Audio and Video-In'
                ] if i2c_for_audio_and_video_in else None,
                'SEG7': v['SEG7'] if seg7 else None,
                'IR': v['IR'] if ir else None,
                'Key': v['Key'] if key else None,
                'Led': v['Led'] if led else None,
                'PS2': v['PS2'] if ps2 else None,
                'SW': v['SW'] if sw else None,
                'Video-In': v['Video-In'] if video_in else None,
                'VGA': v['VGA'] if vga else None,
                'HPS': v['HPS'] if hps else None
            },
            'qpf': {'quartus_version': quartus_version},
            'qsf': {
                'original_quartus_version': (
                    quartus_version
                    if not original_quartus_version
                    else original_quartus_version
                ),
                'last_quartus_version': (
                    quartus_version
                    if not last_quartus_version
                    else last_quartus_version
                ),
                # configurable
                'user_assignments': {
                    'audio': user_assignments['audio'] if audio else None,
                    'clock': user_assignments['clock'] if clock else None,
                    'i2c for audio and video - in': user_assignments[
                        'i2c for audio and video - in'
                    ] if i2c_for_audio_and_video_in else None,
                    'key': user_assignments['key'] if key else None
                },
                # default for De1SoC
                'family': qsf['family'],
                'device': qsf['device'],
                'global_assignments': {
                    'device_filter_package': global_assignments[
                        'device_filter_package'
                    ],
                    'device_filter_pin_count': global_assignments[
                        'device_filter_pin_count'
                    ],
                    'device_filter_speed_grade': global_assignments[
                        'device_filter_speed_grade'
                    ]
                }
            },
            'sdc': {
                'create_clock': sdc['create_clock'] if create_clock else None,
                'create_generated_clock': sdc[
                    'create_generated_clock'
                ] if create_generated_clock else None,
                'set_clock_latency': sdc[
                    'set_clock_latency'
                ] if set_clock_latency else None,
                'set_clock_uncertainty': sdc[
                    'set_clock_uncertainty'
                ] if set_clock_uncertainty else None,
                'set_input_delay': sdc[
                    'set_input_delay'
                ] if set_input_delay else None,
                'set_output_delay': sdc[
                    'set_output_delay'
                ] if set_output_delay else None,
                'set_clock_groups': sdc[
                    'set_clock_groups'
                ] if set_clock_groups else None,
                'set_false_path': sdc[
                    'set_false_path'
                ] if set_false_path else None,
                'set_multicycle_path': sdc[
                    'set_multicycle_path'
                ] if set_multicycle_path else None,
                'set_maximum_delay': sdc[
                    'set_maximum_delay'
                ] if set_maximum_delay else None,
                'set_minimum_delay': sdc[
                    'set_minimum_delay'
                ] if set_minimum_delay else None,
                'set_load': sdc['set_load'] if set_load else None
            }
        })

        self._project_name = project_name
        self._configs = super(DE1SoC, self)._generate(project_name,
                                                      **self.__filtered_static)
        return self

    def generate_files(self,
                       project_name: str=None,
                       project_path: str=None,
                       force: bool=False,
                       **config_filter) -> object:
        """
           Generates FPGA config files for specific project in separate folder.

            :param project_path :type str - specific path to the project
                (default=project_name)
            :param force :type bool - force config to be recreated
            :param config_filter :type dict - allow to customize configs
        """
        return super(DE1SoC, self).generate_files(
            project_name=project_name,
            project_path=project_path,
            force=force,
            **config_filter
        )

    def archive(self,
                project_name: str=None,
                project_path: str=None,
                force: bool=False,
                **config_filter) -> object:
        """ Generate tar file with FPGA config files for specific project """
        return super(DE1SoC, self).archive(
            project_name=project_name,
            project_path=project_path,
            force=force,
            **config_filter
        )
