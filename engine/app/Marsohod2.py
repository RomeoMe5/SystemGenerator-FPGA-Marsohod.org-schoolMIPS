import json
import os

from app import ROOT_DIR
from app.render import Render

M2_STATIC_PATH = os.path.join(ROOT_DIR, "static", "m2.json")


class Marsohod2(Render):
    def __init__(self,
                 path: str=M2_STATIC_PATH,
                 encoding: str="ascii",
                 errors: str="backslashreplace") -> None:
        self._content = None
        with open(path, 'r', encoding=encoding, errors=errors) as fin:
            self._content = json.load(fin)
        super(Marsohod2, self).__init__()

    # TODO: generate configuration files
    def generate(self, project_name: str, path: str, *args, **kwargs) -> ...:
        if os.path.exists(path):
            raise FileExistsError("'{}' already exists".format(path))
        else:
            os.mkdir(path)

        v = super(Marsohod2, self).v(*args, **kwargs)
        qpf = super(Marsohod2, self).qpf(*args, **kwargs)
        qsf = super(Marsohod2, self).qsf(*args, **kwargs)
        sdc = super(Marsohod2, self).sdc(*args, **kwargs)

        with open(os.path.join(path, "{}.v".format(project_name)), 'w') as fout:
            fout.writelines(v)
        with open(os.path.join(path, "{}.qpf".format(project_name)), 'w') as fout:
            fout.writelines(v)
        with open(os.path.join(path, "{}.v".format(project_name)), 'w') as fout:
            fout.writelines(v)
        with open(os.path.join(path, "{}.v".format(project_name)), 'w') as fout:
            fout.writelines(v)
