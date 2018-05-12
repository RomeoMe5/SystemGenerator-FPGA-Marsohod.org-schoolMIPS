from engine.boards.GenericBoard import GenericBoard
from engine.utils.log import LOGGER


class Marsohod3(GenericBoard):

    def __init__(self) -> None:
        super(Marsohod3, self).__init__(self.__class__.__name__)
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
                 tmds: bool=False,
                 ftd: bool=False,
                 ftc: bool=False,
                 io: bool=False,
                 others: bool=False) -> object:
        """ Generates configs for Marsohod3 """
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
                'TMDS': v['TMDS'] if tmds else None,
                'FTD': v['FTD'] if ftd else None,
                'FTC': v['FTC'] if ftc else None,
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
                    'TMDS': user_assignments['TMDS'] if tmds else None,
                    'FTD': user_assignments['FTD'] if ftd else None,
                    'FTC': user_assignments['FTC'] if ftc else None,
                    'IO': user_assignments['IO'] if io else None,
                    'OTHERS': user_assignments['OTHERS'] if others else None
                },

                'family': qsf['family'],
                'device': qsf['device'],
                'global_assignments': {
                    'device_filter_package': global_assignments[
                        'device_filter_package'
                    ]

                    # Doesn't exist in Marsohod3 configuration file

                    # 'device_filter_pin_count': global_assignments[
                    #     'device_filter_pin_count'
                    # ],
                    # 'device_filter_speed_grade': global_assignments[
                    #     'device_filter_speed_grade'
                    # ]
                }
            },
            'sdc': {
                'create_clock': sdc['create_clock'],
                'create_generated_clock': sdc['create_generated_clock'],
                'set_clock_latency':  sdc['set_clock_latency'],
                'set_clock_uncertainty': sdc['set_clock_uncertainty'],
                'set_input_delay': sdc['set_input_delay'],
                'set_output_delay': sdc['set_output_delay'],
                'set_clock_groups': sdc['set_clock_groups'],
                'set_false_path': sdc['set_false_path'],
                'set_multicycle_path': sdc['set_multicycle_path'],
                'set_maximum_delay': sdc['set_maximum_delay'],
                'set_minimum_delay': sdc['set_minimum_delay'],
                'set_load': sdc['set_load']
            }
        })

        self._project_name = project_name
        self._configs = super(Marsohod3, self)._generate(project_name,
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
        return super(Marsohod3, self).generate_files(
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
        return super(Marsohod3, self).archive(
            project_name=project_name,
            project_path=project_path,
            force=force,
            **config_filter
        )
