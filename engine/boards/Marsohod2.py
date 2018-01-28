import logging
import os

from engine.utils.load import get_static_path, load_json, load_plain_text
from engine.utils.prepare import create_dirs
from engine.utils.render import Render

try:
    from configs.engine import CONFIG
except ImportError as err:
    logging.warning("Can't import configuration!\n%s", err)
    from engine.utils import Config as CONFIG


class Marsohod2(Render):
    def __init__(self) -> None:
        self.path = get_static_path(
            self.__class__.__name__,
            CONFIG.STATIC_EXTENSION
        )
        self._static_content = load_json(
            self.path,
            encoding=CONFIG.FILE_ENCODING,
            errors=CONFIG.FILE_ERRORS
        )
        self._license = load_plain_text(
            os.path.join(CONFIG.PATHS['static'], "LICENSE"),
            encoding=CONFIG.FILE_ENCODING,
            errors=CONFIG.FILE_ERRORS
        )
        super(Marsohod2, self).__init__()

    def generate(self,
                 project_name: str,
                 path: str=CONFIG.DESTINATION_PATH,
                 **kwargs) -> None:
        create_dirs(path, rewrite=False)

        config_files = {
            'v': super(Marsohod2, self).v(project_name=project_name, **kwargs),
            'qpf': super(Marsohod2, self).qpf(**kwargs),
            'qsf': super(Marsohod2, self).qsf(**kwargs),
            'sdc': super(Marsohod2, self).sdc(**kwargs)
        }

        for extension, content in config_files.items():
            with open(os.path.join(
                    path, ".".join((project_name, extension))), 'w') as fout:
                logging.info("Creating '%s'...", fout.name)
                for line in content:
                    fout.write(line)

        with open(os.path.join(path, "LICENSE"), 'w') as fout:
            logging.debug("Adding LICENSE: '%s'.", fout.name)
            fout.write(self._license)
