from engine.boards.GenericBoard import GenericBoard
from engine.utils.log import LOGGER


class Marsohod2B(GenericBoard):
    """ Marsohod2Bis configs generator """

    def __init__(self) -> None:
        super(Marsohod2B, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS IS UNDER DEVELOPMENT: NO WARRANTY PROVIDED!"
        LOGGER.warning(self.message)

    def generate(self,
                 project_name: str,
                 # qpf: optional
                 quartus_version: str="15.1.0",
                 # qsf: optional
                 original_quartus_version: str=None,  # default=quartus_version
                 last_quartus_version: str=None,  # default=quartus_version
                 # qsf-v
                 ftdi: bool=False,
                 clock: bool=False,
                 keys: bool=False,
                 sdram: bool=False,
                 leds: bool=False,
                 vga: bool=False,
                 adc: bool=False,
                 io: bool=False,
                 others: bool=False) -> object:
        """ Generates configs for Marsohod2B """
        qsf = self._static['qsf']
        global_assignments = qsf['global_assignments']
        user_assignments = qsf['user_assignments']
        qpf = self._static['qpf']
        sdc = self._static['sdc']
        v = self._static['v']['assigments']  # warning: may be changed

        self.__filtered_static = self._filter_none(**{
            'v': {'assigments': {
                'FTDI': v['FTDI'] if ftdi else None,
                'CLOCK': v['CLOCK'] if clock else None,
                'KEY': v['KEY'] if keys else None,
                'SDRAM': v['SDRAM'] if sdram else None,
                'LED': v['LED'] if leds else None,
                'VGA': v['VGA'] if vga else None,
                'ADC': v['ADC'] if adc else None,
                'IO': v['IO'] if io else None,
                'OTHERS': v['OTHERS'] if others else None
            }},
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
                    'FTDI': user_assignments['FTDI'] if ftdi else None,
                    'CLOCK': user_assignments['CLOCK'] if clock else None,
                    'KEY': user_assignments['KEY'] if keys else None,
                    'SDRAM': user_assignments['SDRAM'] if sdram else None,
                    'LED': user_assignments['LED'] if leds else None,
                    'VGA': user_assignments['VGA'] if vga else None,
                    'ADC': user_assignments['ADC'] if adc else None,
                    'IO': user_assignments['IO'] if io else None,
                    'OTHERS': user_assignments['OTHERS'] if others else None
                },

                'family': qsf['family'],
                'device': qsf['device'],
                'global_assignments': {
                    'device_filter_package': global_assignments[
                        'device_filter_package'
                    ]

                    # Doesn't exist in Marsohod2B configuration file

                    # 'device_filter_pin_count': global_assignments[
                    #     'device_filter_pin_count'
                    # ],
                    # 'device_filter_speed_grade': global_assignments[
                    #     'device_filter_speed_grade'
                    # ]
                }
            }
        })

        self._project_name = project_name
        self._configs = super(Marsohod2B, self)._generate(project_name,
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
        return super(Marsohod2B, self).generate_files(
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
        return super(Marsohod2B, self).archive(
            project_name=project_name,
            project_path=project_path,
            force=force,
            **config_filter
        )

    @property
    def params(self) -> dict:
        """ Configurable params. """
        # sdc isn't included, because it should be generated atomaitcally
        return {
            'str': ("project_name", "quartus_version"),
            'bool': ("ftdi", "clock", "keys", "sdram", "leds",
                     "vga", "adc", "io", "others")
        }
