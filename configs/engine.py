""" Configuration for engine """

import logging
import os

from engine.utils import Config
from engine.utils.log import enable_logging_to_file

CONFIG = Config(
    BASE_DIR=os.path.dirname(__file__),
    LOG_MAXBYTES=1024 * 10,
    LOG_BACKUPCOUNT=10,
    LOG_FORMAT="[%(asctime)s] %(levelname)s "
               "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s",
    LOG_DATE_FMT="%H:%M:%S",
    LOG_LEVEL=logging.DEBUG,
    LOG_RESULT=True,
    LOG_ARGS=True,
    LOG_KWARGS=True,
    FILE_ENCODING="utf-8",
    STATIC_EXTENSION="json",
    COPYRIGHT="Moscow University of Electronics and Mathematics, "
              "Higher School for Economics University",
    FALLBACK_EXTENSION="jinja"
)

logging.basicConfig(level=CONFIG.LOG_LEVEL,
                    format=CONFIG.LOG_FORMAT,
                    datefmt=CONFIG.LOG_DATE_FMT)

CONFIG["LOG_PATH"] = os.path.join(CONFIG.BASE_DIR, "logs")
CONFIG["LOG_FILE"] = os.path.join(CONFIG.LOG_PATH, "app.log")
CONFIG["LOG_USE_LOGGER"] = enable_logging_to_file(
    path=CONFIG.LOG_PATH,
    file=CONFIG.LOG_FILE,
    max_bytes=CONFIG.LOG_MAXBYTES,
    backup_count=CONFIG.LOG_BACKUPCOUNT,
    fmt=CONFIG.LOG_FORMAT,
    level=CONFIG.LOG_LEVEL,
    logger=logging.getLogger("$global")
)
