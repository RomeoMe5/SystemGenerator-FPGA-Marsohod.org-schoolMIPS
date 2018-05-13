import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask_babel import lazy_gettext as _l

try:
    from config import LOG_LEVEL, LOG_FORMAT
except ImportError as err:
    LOG_LEVEL = logging.WARNING
    LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:" \
        "%(lineno)d] %(message)s"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt="%H:%M:%S")


def enable_email_error_notifications(app: object,
                                     level: int=logging.ERROR) -> bool:
    if app.debug or not app.config.get('MAIL_SERVER'):
        return False

    auth = (app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
    if not any(auth):
        auth = None

    mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
        toaddrs=app.config.get('ADMINS'),
        subject=_l("Microblog Failure"),
        credentials=auth,
        secure=() if int(app.config.get('MAIL_USE_TLS')) else None
    )
    mail_handler.setLevel(level)

    app.logger.addHandler(mail_handler)
    return True


def enable_logging_to_file(app: object, level: int=logging.INFO) -> bool:
    if app.debug:
        return False

    logs_path = app.config.get('LOG_PATH', "logs")
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)

    file_handler = RotatingFileHandler(
        app.config.get('LOG_FILE', os.path.join(logs_path, "app.log")),
        maxBytes=app.config.get('LOG_MAXBYTES', 1024 * 100),
        backupCount=app.config.get('LOG_BACKUPCOUNT', 10)
    )
    file_handler.setFormatter(logging.Formatter(app.config.get('LOG_FORMAT',
                                                               LOG_FORMAT)))
    file_handler.setLevel(level)
    app.logger.addHandler(file_handler)

    app.logger.debug("Logging to file setup successfully.")
    return True


def enable_logging_to_stdout(app: object, level: int=logging.INFO) -> bool:
    if app.debug:
        return False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(app.config.get('LOG_FORMAT',
                                                                 LOG_FORMAT)))
    stream_handler.setLevel(level)
    app.logger.addHandler(stream_handler)

    app.logger.debug("Logging to stdout setup successfully.")
    return True
