"""
    Generate configs for Marsohod3 board
"""

import sys
import os

from engine import Board

sys.path.append(os.getcwd())
if __name__ == "__main__":
    # it's possible specify project name as first script's positional argument
    project_name = "tmp" if len(sys.argv) < 2 else sys.argv[1]

    # generate empty project and save it
    board = Board("Marsohod3").generate(project_name).dump(project_name)
    board.reset()  # reset board to full setup
    # generate project with keys support and save it with path == project name
    board.setup(flt={'key': True, 'led': True, 'clock': True},
                func={'Seven': True, 'Uart8': True},
                mips_type='simple').generate().dump()
    # regenerate project with keys and Seven func and
    # arcive generated project with path == project name
    board.generate(flt={'key': True, 'led': True, 'clock': True},
                   func={'Seven': True, 'Uart8': True},
                   mips_type='simple').archive()
