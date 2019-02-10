import os
import re


class PATHS(object):
    ROOT = os.path.dirname(__file__)
    BASE = os.path.abspath(os.path.dirname(ROOT))
    STATIC = os.path.join(ROOT, "static")
    TEMPL = os.path.join(ROOT, "templates")
    MIPS = os.path.join(STATIC, "school_mips")


class DESTINATIONS(object):
    OUTPUT = "output_files"
    FUNC = "functions"
    MIPS = "mips"


class MIPS(object):
    CONFIG = "SchoolMips.yml"
    VERSIONS = (
        "simple",
        "mmio",
        "irq",
        "pipeline",
        "pipeline_irq",
        "pipeline_ahb"
    )


# native supported boards
BOARDS = ("marsohod2", "marsohod2b", "marsohod3", "marsohod3b", "de1soc")


class FUNCTIONS(object):
    ITEMS = {
        'ButtonDebouncer': "Button Debouncer: add delay between button inputs",
        'Demultiplexer': "Simple Demultiplexer",
        'Generator': "Frequency Generator: decrease internal board clock rate",
        'Seven': "7-segment indicator controller",
        'Uart8': "Simple 8-bit UART"
    }
    PARAMS = {
        'delay': "Delay",
        'width': "Input Width",
        'out_freq': "Output Frequency",
        'baud_rate': "Board Baud Rate"
    }


DEFAULT_PROJECT_NAME = "MyFpgaProject"

PROJECT_NAME_PATTERN = re.compile(r"^[a-zA-Z][0-9a-zA-Z_]*$")
