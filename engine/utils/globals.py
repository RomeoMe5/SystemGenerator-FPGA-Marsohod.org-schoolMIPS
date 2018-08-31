import json
import os

import dill
import yaml


# static class
class PATHS:
    ROOT = os.path.dirname(os.path.dirname(__file__))


# add path relative to the project root to class globals
PATHS.BASE = os.path.abspath(os.path.dirname(PATHS.ROOT))
PATHS.STATIC = os.path.join(PATHS.ROOT, "static")
PATHS.TEMPL = os.path.join(PATHS.ROOT, "templates")
PATHS.MIPS = os.path.join(PATHS.STATIC, "school_mips")

# for configs, in order of significance (priority)
# [feature] TODO: add "xml", "csv"
SUPPORTED_EXTENSIONS = ("yml", "json", "bin")
SUPPORTED_LOADERS = {
    'yml': yaml.load,
    'json': json.load,
    'bin': dill.load
}
