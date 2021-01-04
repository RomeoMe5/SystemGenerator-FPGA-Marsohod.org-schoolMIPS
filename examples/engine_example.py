"""
    This file describes common usage scenarios for 'engine' part
    of the project and can be used in debug purposes.
"""

from engine import BOARDS, Board
import os
import sys
from pprint import pprint

sys.path.append(os.getcwd())


if __name__ == "__main__":
    # It's possible specify project name as first script's positional argument.
    project_name = None if len(sys.argv) < 2 else sys.argv[1]

    model = BOARDS[0]

    # Common 'engine' usage scenario (lifecycle).
    # This uses default parameters for all configurable values.
    board = Board(model)  # 0 : initializing
    _ = board.setup(project_name=project_name)  # 1 : configuring
    _ = board.generate()  # 2 : generating project files
    _ = board.dump()  # 3.1 : output as project (directory with files)
    _ = board.archive()  # 3.2 : output as archive (packed project)
    _ = board.reset()  # 4 : reload board configuration from static file

    # Generated content of project files can also be found
    # in 'configs' property of Board instance.

    # The same can also be performed as a chain of methods calls
    # (or even just as a sinle line of code).
    board = (Board(model)
             .setup(project_name=project_name)
             .generate()
             .dump()
             .archive()
             .reset())

    # It's possible to setup which hardware to include in a project
    # by specifying a filter for configs.
    # All configurable parameters can be found in 'params' property.
    configs_filter = {
        'key': True,
        'led': True,
        'clock': True
    }
    functions_to_include = {
        'Seven': True,
        'Uart8': True
    }

    # Step #1 of Board instance lifecycle can be skipped
    # as 'generate' method supports almost all functions
    # of project configuration.

    # It's also possible to specify path for saving project
    # by 'path' argument of 'dump' or 'archive' methods.
    # The default behaviour of this methods is to use project name
    # as path to saving project.

    # Generate project in concordance with filter and
    # save it with path == project name (same as default behaviour).
    board.generate(flt=configs_filter,
                   func=functions_to_include).dump(path=project_name)

    # There are a possibility to include SchoolMIPS core into
    # the generated project by specifying version of this core
    # through 'mips_type' argument.
    # More information for SchoolMIPS can be found in official documentation:
    # https://github.com/MIPSfpga/schoolMIPS/wiki

    # Regenerate project in concordance with filter, include SchoolMIPS core
    # and arcive generated project with path == project name.
    board.generate(flt=configs_filter,
                   func=functions_to_include,
                   mips_type='simple').archive(path=project_name)
