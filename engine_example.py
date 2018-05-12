import logging
import sys

# suspend engine logs
logging.basicConfig(level=logging.ERROR)

from engine import DE1SoC


if __name__ == "__main__":
    # it's possible specify project name as first script's positional argument
    project_name = "tmp" if len(sys.argv) < 2 else sys.argv[1]

    # generate empty project
    print(DE1SoC().generate_files(project_name))

    # generate project with audio support
    board = DE1SoC().generate(project_name + "1", audio=True).dump()

    # regenerate project with audio and clock support
    board.archive(project_name + "1", force=True, audio=True, clock=True)
