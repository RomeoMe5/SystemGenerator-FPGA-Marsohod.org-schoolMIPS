# [minor] TODO remove env usage for prod
import logging
import os
from typing import NoReturn

from dotenv import load_dotenv
from flask import Flask


APP_NAME = "FPGA-Generator"
CURR_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(CURR_DIR)
load_dotenv(os.path.join(CURR_DIR, ".env"))


class Config(object):
    DEBUG = False
    TESTING = False

    APP_HEADER = "HSE FPGA Generator"
    ADMIN_EMAIL = "hell03end@outlook.com"
    SECRET_KEY = "no-one-knows"
    ELASTICSEARCH_URL = None

    # [future] TODO replace to Postgres/MySQL
    DB_PATH = os.path.join(BASE_DIR, f"{APP_NAME}.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.1

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "hell03end@gmail.com"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_ADMINS = (ADMIN_EMAIL, MAIL_USERNAME)
    MAIL_SENDER = f"{APP_HEADER} Admin <{MAIL_USERNAME}>"

    LOG_NAME = f"{APP_NAME}.log"
    LOG_PATH = os.path.join(BASE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_PATH, LOG_NAME)
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = "[%(asctime)s] %(levelname)s " \
        "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s"
    LOG_MAXBYTES = 1024 * 100
    LOG_BACKUPCOUNT = 10
    LOG_TO_STDOUT = False
    LOG_TO_FILE = True

    LANGUAGES = ("ru", "en")
    ITEMS_PER_PAGE = 25
    TOKEN_TTL = 60 * 60 * 24  # expires in one day
    SSL_REDIRECT = True


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_TO_STDOUT = True
    LOG_TO_FILE = True
    ITEMS_PER_PAGE = 5
    TOKEN_TTL = 60 * 5  # expires in 5 minutes
    SSL_REDIRECT = False


class TestingConfig(DevelopmentConfig):
    TESTING = True
    LOG_TO_FILE = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SERVER_NAME = "fpga-generator.hse.ru"


configs = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
