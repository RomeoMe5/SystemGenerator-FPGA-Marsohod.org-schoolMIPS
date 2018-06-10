""" Supported boards. """

from engine.boards.De1SoC import De1SoC
from engine.boards.ManualBoard import ManualBoard
from engine.boards.Marsohod2 import Marsohod2
from engine.boards.Marsohod2B import Marsohod2B
from engine.boards.Marsohod3 import Marsohod3
from engine.boards.Marsohod3B import Marsohod3B

# all supported boards
BOARDS = ("Marsohod2", "Marsohod2B", "Marsohod3", "Marsohod3B")  # "De1SoC"

# De1SoC is not icluded because it's usage is depreciated
__all__ = ("ManualBoard", *BOARDS)
