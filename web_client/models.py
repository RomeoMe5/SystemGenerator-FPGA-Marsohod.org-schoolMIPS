# [feature] TODO: add table for static files

import os
from datetime import datetime
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from web_client import BASE_DIR, db, login_manager
from web_client.utils import get_gravatar_url


class User(UserMixin, db.Model):
    """ Represents user of the system. """

    id = db.Column(db.Integer, primary_key=True)
    _email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    _password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def path(self) -> str:
        return os.path.join(current_app.config['STATIC_PATH'],
                            self._email.split('@')[0])

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str) -> None:
        self._email = email.strip().lower()

    # Is needed for backward compitability
    @property
    def password(self) -> None:
        return

    @password.setter
    def password(self, password: str) -> None:
        """ Set's password hash for current user. """
        self._password_hash = generate_password_hash(password)

    def avatar(self, size: int=80) -> str:
        """ Get link to user picture in gravatar. """
        return get_gravatar_url(self._email, size=size)

    def check_password(self, password: str) -> bool:
        """ Verify password is correct for current user. """
        return check_password_hash(self._password_hash, password)

    def get_verification_token(self,
                               expires_in: float or int=60 * 60 * 24,
                               encoding: str="utf-8") -> str:
        """ Generate verification token for general proposes. """
        return jwt.encode(
            {
                'verification': self.id,
                'exp': time() + expires_in
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        ).decode(encoding)

    @staticmethod
    def verify_token(token: bytes) -> object or None:
        """ Check verification token is correct for current user. """
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['verification']
            return User.query.get(user_id)
        except BaseException as err:
            current_app.logger.info("Invalid token:\n%s", err)

    def __repr__(self) -> str:
        return f"<User: {self.email}>"


class BlogPost(db.Model):
    """ Represents user of the system. """

    id = db.Column(db.Integer, primary_key=True)
    _link = db.Column(db.String(325), index=True, unique=True)
    title = db.Column(db.String(255), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def link(self) -> str:
        time = self.timestamp.strftime("%Y%m%d-%H%M%S")
        return "-".join(("-".join(self.title.lower().split()), time))

    @property
    def rel_path(self) -> str or None:
        return "blog/pages/" + self.link + ".html"

    @property
    def path(self) -> str or None:
        file_path = os.path.join(BASE_DIR, "templates", self.rel_path)
        if os.path.exists(file_path):
            return file_path

    @property
    def date(self) -> str:
        return self.timestamp.strftime("%d/%m/%Y %H:%M")

    def __repr__(self) -> str:
        return f"<Article: {self.link}>"


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """ Get current user from db if it's exists. """
    return User.query.get(int(user_id))
