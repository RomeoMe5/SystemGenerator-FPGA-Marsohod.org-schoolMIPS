import os


class PATHS:
    ROOT = os.path.dirname(__file__)
    TEMPL = os.path.join(ROOT, "templates")


class DESTINATIONS:
    OUTPUT = "output_files"
    FUNC = "functions"
    MIPS = "mips"


class MIPS:
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
BOARDS = ("marsohod2", "marsohod2b", "marsohod3", "marsohod3b")  # "de1soc"

FUNCTIONS = {
    'ButtonDebouncer': "Button Debouncer: add delay between button inputs",
    'Demultiplexer': "Simple Demultiplexer",
    'Generator': "Frequency Generator: decrease internal board clock rate",
    'Seven': "7-segment indicator controller",
    'Uart8': "Simple 8-bit UART"
}

DEFAULT_PROJECT_NAME = "my-project"
