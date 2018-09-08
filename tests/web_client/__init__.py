import os
from typing import NoReturn

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from configs.web_client import Config
from web_client import create_app
from web_client.models import BackupableMixin


MOCK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock")
mock_db = SQLAlchemy()


def commit_or_rollback(db: SQLAlchemy) -> NoReturn:
    try:
        db.session.commit()
    except BaseException as exc:
        db.session.rollback()
        raise exc


class MockConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    ELASTICSEARCH_URL = None


def create_mock_app(db: SQLAlchemy, name: str="test") -> Flask:
    return create_app(config_class=MockConfig, db=db, name=name)


class MockModel(BackupableMixin, mock_db.Model):
    __tablename__ = "mockmodel"
    id = mock_db.Column(mock_db.Integer, primary_key=True)

    data = mock_db.Column(mock_db.String(16))
