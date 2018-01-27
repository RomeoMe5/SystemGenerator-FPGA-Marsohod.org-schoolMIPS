import os
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape

import engine

PATHS = {'root': os.path.dirname(engine.__file__)}
PATHS['static'] = os.path.join(PATHS['root'], "static")
PATHS['templ'] = os.path.join(PATHS['root'], "templates")

FILE_ENCODING = "utf-8"

ENV = Environment(
    loader=FileSystemLoader(PATHS['templ'], encoding=FILE_ENCODING),
    autoescape=select_autoescape(enabled_extensions=(), default=False),
    trim_blocks=True,
    lstrip_blocks=True,
    newline_sequence="\r\n" if "win" in sys.platform else "\n",
    keep_trailing_newline=True,
    auto_reload=False
)
