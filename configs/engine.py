""" Configuration for fpga_marsohod_generator_engine """

import logging
import os
from logging.handlers import RotatingFileHandler

COPYRIGHT = "Moscow University of Electronics and Mathematics, " \
            "Higher School for Economics University"
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# ===== Logging =====
LOG_LEVEL = logging.DEBUG
LOG_NAME = "fpga_marsohod_generator_engine.log"
LOG_PATH = os.path.join(BASE_DIR, "logs")
LOG_FORMAT = (
    "%(asctime)s.%(msecs)d [%(name)s:%(filename)s.%(funcName)s:%(lineno)d] "
    "%(levelname)s %(message)s"
)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt="%H:%M:%S")
LOGGER = logging.getLogger(LOG_NAME)

if not os.path.exists(LOG_PATH):
    logging.debug("Create path for logging: '%s'.", LOG_PATH)
    os.mkdir(LOG_PATH)
else:
    logging.debug("'%s' already exists!", LOG_PATH)

FILE_HANDLER = RotatingFileHandler(
    os.path.join(LOG_PATH, LOG_NAME),
    maxBytes=1024 * 100,
    backupCount=10
)
FILE_HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))
FILE_HANDLER.setLevel(LOG_LEVEL)
LOGGER.addHandler(FILE_HANDLER)
