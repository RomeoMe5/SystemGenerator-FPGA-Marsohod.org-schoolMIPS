import logging
import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
STATIC_PATH = os.path.join(BASE_DIR, os.environ.get('STATIC_PATH', '.gen'))

LOG_FORMAT = "[%(asctime)s] %(levelname)s " \
    "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s"
LOG_LEVEL = logging.DEBUG


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', "no-one-knows")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = int(os.environ.get('MAIL_USE_TLS', False))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [MAIL_USERNAME]

    LOG_NAME = f"{__name__}.log"
    LOG_PATH = os.path.join(BASE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_PATH, LOG_NAME)
    LOG_FORMAT = LOG_FORMAT
    LOG_LEVEL = LOG_LEVEL
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT", False)
    LOG_MAXBYTES = 1024 * 100
    LOG_BACKUPCOUNT = 10

    LANGUAGES = ["en", "ru"]

    STATIC_PATH = STATIC_PATH
