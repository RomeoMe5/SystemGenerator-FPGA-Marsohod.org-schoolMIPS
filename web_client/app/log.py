import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
           " %(message)s",
    datefmt="%H:%M:%S"
)


def enable_logging_to_file(app: object, level: int=logging.INFO) -> bool:
    if app.debug:
        return False

    logs_path = app.config.get('LOG_PATH', "logs")
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)

    file_handler = RotatingFileHandler(
        app.config.get('LOG_FILE', os.path.join(logs_path, "app.log")),
        maxBytes=app.config.get('LOG_MAXBYTES', 1024 * 10),
        backupCount=app.config.get('LOG_BACKUPCOUNT', 10)
    )
    file_handler.setFormatter(logging.Formatter(app.config.get(
        'LOG_FORMAT',
        "%(asctime)s [%(levelname)s]: %(message)s [%(pathname)s:%(lineno)d]"
    )))
    file_handler.setLevel(level)
    app.logger.addHandler(file_handler)

    app.logger.info("Initial log message.")
