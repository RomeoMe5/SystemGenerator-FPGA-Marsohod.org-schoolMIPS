""" Configuration for WEB client """
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', "you-will-never-guess")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_PATH = os.path.join(BASE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_PATH, "app.log")
    LOG_MAXBYTES = 10240
    LOG_BACKUPCOUNT = 10
    LOG_FORMAT = "[%(asctime)s] %(levelname)s " \
        "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s"
