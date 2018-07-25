import logging
import os

from dotenv import load_dotenv

CURR_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(CURR_DIR)
load_dotenv(os.path.join(CURR_DIR, ".env"))

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "[%(asctime)s] %(levelname)s " \
    "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s"


class Config(object):
    DEBUG = True

    SECRET_KEY = "no-one-knows"

    DB_URI = f"sqlite:///{os.path.join(BASE_DIR, "app.db")}"
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "hell03end@gmail.com"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ("hell03end@outlook.com", MAIL_USERNAME)

    LOG_PATH = os.path.join(BASE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_PATH, f"{__name__}.log")
    LOG_FORMAT = LOG_FORMAT
    LOG_LEVEL = LOG_LEVEL
    LOG_TO_STDOUT = False
    LOG_MAXBYTES = 1024 * 100
    LOG_BACKUPCOUNT = 10
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    LANGUAGES = ("ru", "en")

    TOKEN_TTL = 60 * 60 * 24  # expires in one day
