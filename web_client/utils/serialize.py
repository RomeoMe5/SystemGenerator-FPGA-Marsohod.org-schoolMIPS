import os
import pickle
from typing import Iterable, NoReturn

from flask import current_app
from flask_sqlalchemy import SQLAlchemy

from web_client import db


class Serializer(object):
    @staticmethod
    def dump(path: str, *models) -> NoReturn:
        if os.path.exists(path):
            current_app.logger.warning("Path already exists: %s", path)
        payload = [model.dump() for model in models]
        with open(path, "wb") as fout:
            pickle.dump(payload, fout)

    @staticmethod
    def load(path: str, *models, db: SQLAlchemy=db) -> NoReturn:
        if not os.path.exists(path):
            current_app.logger.error("Path isn't exist: %s", path)
            return
        with open(path, "rb") as fin:
            for model, payload in zip(models, pickle.load(fin)):
                model.load(payload, db=db)
        db.session.commit()

    @staticmethod
    def show(path: str) -> Iterable:
        if not os.path.exists(path):
            current_app.logger.error("Path isn't exist: %s", path)
            return
        with open(path, "rb") as fin:
            return pickle.load(fin)
