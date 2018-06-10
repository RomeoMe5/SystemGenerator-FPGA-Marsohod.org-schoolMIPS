import sys

from engine import Marsohod3


if __name__ == "__main__":
    # it's possible specify project name as first script's positional argument
    project_name = "tmp" if len(sys.argv) < 2 else sys.argv[1]

    # generate empty project
    print(Marsohod3().generate_files(project_name))

    # generate project with keys support
    board = Marsohod3().generate(project_name + "1", keys=True).dump()

    # regenerate project with keys and clock support
    board.archive(project_name + "1", force=True, keys=True, clock=True)
