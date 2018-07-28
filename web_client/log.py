import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler
from typing import NoReturn

from flask import Flask
from flask_babel import lazy_gettext as _l


def enable_email_error_notifications(app: Flask,
                                     level: int=logging.ERROR,
                                     fmt: str=None) -> NoReturn:
    auth = (app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
    if not any(auth):
        auth = None

    mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
        toaddrs=app.config.get('ADMINS'),
        subject=_l("HSE FPGAMarsohodCAD Failure"),
        credentials=auth,
        secure=() if int(app.config.get('MAIL_USE_TLS')) else None
    )
    mail_handler.setLevel(level)
    if fmt:
        mail_handler.setFormatter(logging.Formatter(fmt))

    app.logger.addHandler(mail_handler)


def enable_logging_to_file(app: Flask,
                           level: int=logging.INFO,
                           fmt: str=None,
                           path: str="logs",
                           filename: str="app.log",
                           max_bytes: int=1024*100,
                           backup_count: int=10) -> NoReturn:
    if not os.path.exists(path):
        os.mkdir(path)

    file_handler = RotatingFileHandler(
        os.path.join(path, filename),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    if fmt:
        file_handler.setFormatter(logging.Formatter(fmt))
    app.logger.addHandler(file_handler)


def enable_logging_to_stdout(app: Flask,
                             level: int=logging.INFO,
                             fmt: str=None) -> NoReturn:
    stream_handler = logging.StreamHandler()
    if fmt:
        stream_handler.setFormatter(logging.Formatter(fmt))
    stream_handler.setLevel(level)
    app.logger.addHandler(stream_handler)
