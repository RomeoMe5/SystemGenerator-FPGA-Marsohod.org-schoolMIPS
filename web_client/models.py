import os
import shutil
from datetime import datetime
from enum import Enum
from time import time
from typing import Dict, Iterable, NoReturn

import jwt
import markdown as md
from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import escape, secure_filename

from web_client import PATHS, db, login_manager
from web_client.utils.misc import INVALID_CHARS, get_gravatar_url, get_uri


EDITED_TIMEOUT = 1


def setup_is_edited(obj: object) -> NoReturn:
    if not obj.create_dt:
        return
    if (datetime.utcnow() - obj.create_dt).total_seconds() > EDITED_TIMEOUT:
        obj.edited_dt = datetime.utcnow()


def render_as_markdown(text: str) -> str:
    return md.markdown(escape(text), output_format="html5")


class BackupableMixin(object):
    """ Implements backup of model fields. """

    def _asdict(self) -> Dict[str, object]:
        payload = self.__dict__.copy()
        # due to uncommited items
        if "_sa_instance_state" in payload:
            del payload['_sa_instance_state']
        return payload

    def _fromdict(self, dump: Dict[str, object]) -> object:
        for field, value in dump.items():
            setattr(self, field, value)
        return self

    @classmethod
    def dump(cls) -> Iterable[Dict[str, object]]:
        try:
            return [obj._asdict() for obj in cls.query.all()]
        except BaseException as exc:
            current_app.logger.warning("Can't dump model %s:\n%s", cls, exc)
            return []

    @classmethod
    def load(cls,
             dumps: Iterable[Dict[str, object]],
             db: SQLAlchemy=db) -> NoReturn:
        for dump in dumps:
            db.session.add(cls()._fromdict(dump))


class Permissions(Enum):
    ADMIN = 10
    MODERATOR = 5
    USER = 1


file_dirs = db.Table(
    "file_dirs",
    db.Model.metadata,
    db.Column("file_id", db.Integer, db.ForeignKey("file.id")),  # left
    db.Column("dir_id", db.Integer, db.ForeignKey("file.id"))  # right
)


class Comment(BackupableMixin, db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)

    _text = db.Column(db.Text, nullable=False)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    del_dt = db.Column(db.DateTime, index=True)
    edited_dt = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    @property
    def is_deleted(self) -> bool:
        return self.del_dt is not None

    @is_deleted.setter
    def is_deleted(self, value: bool) -> NoReturn:
        self.del_dt = datetime.utcnow() if value else None

    @property
    def is_edited(self) -> bool:
        return self.edited_dt is not None

    @property
    def text(self) -> str:
        return render_as_markdown(self._text)

    @property
    def raw_text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> NoReturn:
        if self._text != value.strip():
            self._text = value.strip()
            setup_is_edited(self)

    def __repr__(self) -> str:
        return f"<Comment[{self.id}]: {self.create_dt}, {self._text}>"


# [future] TODO finish File model
class File(BackupableMixin, db.Model):
    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)

    _name = db.Column(db.String(64), nullable=False, index=True)
    uri = db.Column(db.String(64), nullable=False, unique=True, index=True)
    _path = db.Column(db.String(64), nullable=False, unique=True, index=True)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_dir = db.Column(db.Boolean, nullable=False, default=False)

    _size = db.Column(db.Integer)
    load_count = db.Column(db.Integer, default=0)

    files = db.relationship(
        "File",
        secondary=file_dirs,
        primaryjoin=(file_dirs.c.file_id == id),
        secondaryjoin=(file_dirs.c.dir_id == id),
        backref=db.backref("dirs", lazy="dynamic"),
        lazy="dynamic"
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @property
    def size(self) -> float:
        return self._size / 1024  # in bytes

    @size.setter
    def size(self, value: int) -> NoReturn:
        if value > 0:
            self._size = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> NoReturn:
        self._name = secure_filename(os.path.basename(value))
        self.uri = get_uri(value)
        while File.query.filter_by(uri=self.uri).first() is not None:
            self.uri = get_uri(value)

    @property
    def path(self) -> str:
        return os.path.join(PATHS.FILES, self._path)

    @path.setter
    def path(self, value: str) -> NoReturn:
        self._path = value.strip()

    @staticmethod
    def remove_dir(items: Iterable) -> NoReturn:
        for item in items:
            if item.is_dir:
                File.remove_dir(item.files)
            else:
                db.session.delete(item)
                os.remove(item.path)

    def delete(self) -> NoReturn:
        if self.is_dir:
            self.remove_dir(self.files)
            shutil.rmtree(self.path)
        else:
            os.remove(self.path)
        db.session.delete(self)

    def __repr__(self) -> str:
        return f"<File[{self.id}]: {self.name}, {self.uri}, {self.load_count}>"


class Image(BackupableMixin, db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)

    _name = db.Column(db.String(128), nullable=False, index=True)
    uri = db.Column(db.String(64), nullable=False, unique=True, index=True)
    load_count = db.Column(db.Integer, nullable=False, default=0)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    fmt = db.Column(db.String(8))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @property
    def link(self) -> str:
        self.load_count += 1
        return self.uri

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> NoReturn:
        self.fmt = value.strip().lower().split('.')[-1]
        self._name = secure_filename(os.path.basename(value))
        if self.uri:
            return
        self.uri = get_uri(value)
        while Image.query.filter_by(uri=self.uri).first() is not None:
            self.uri = get_uri(value)

    def __repr__(self) -> str:
        return (f"<Image[{self.id}]: {self.name}, {self.uri}>")


class Post(BackupableMixin, db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)

    _title = db.Column(db.String(140), nullable=False, index=True, unique=True)
    _text = db.Column(db.Text, nullable=False)
    uri = db.Column(db.String(325), nullable=False, index=True, unique=True)
    watch_count = db.Column(db.Integer, nullable=False, default=0)
    visible = db.Column(db.Boolean, nullable=False, index=True, default=True)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    edited_dt = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    @property
    def is_edited(self) -> bool:
        return self.edited_dt is not None

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> NoReturn:
        if self._title != value.strip():
            self._title = value.strip()
            setup_is_edited(self)
        if self.uri:
            return
        if self.create_dt is None:
            self.create_dt = datetime.utcnow()
        self.uri = "-".join((
            "-".join(INVALID_CHARS.sub(value.strip().lower(), '').split()),
            self.create_dt.strftime("%Y%m%d-%H%M%S")
        ))

    @property
    def text(self) -> str:
        return render_as_markdown(self._text)

    @property
    def raw_text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> NoReturn:
        if self._text != value.strip():
            self._text = value.strip()
            setup_is_edited(self)

    def delete(self) -> NoReturn:
        for comment in self.comments:
            db.session.delete(comment)
        db.session.delete(self)

    def __repr__(self) -> str:
        return f"<Post[{self.id}]: {self.uri}, {self.watch_count}>"


class User(UserMixin, BackupableMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    _email = db.Column(db.String(128), nullable=False, index=True, unique=True)
    _phone = db.Column(db.String(12), nullable=False, index=True, unique=True)
    _password_hash = db.Column(db.String(128), nullable=False)
    _permission_level = db.Column(db.Integer, nullable=False, index=True,
                                  default=Permissions.USER.value)
    reg_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    name = db.Column(db.String(64))
    del_dt = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    _city = db.Column(db.String(64), index=True)
    del_reason = db.Column(db.String(256))
    course = db.Column(db.Integer)
    university = db.Column(db.String(128))
    faculty = db.Column(db.String(128))

    posts = db.relationship("Post", backref="author", lazy="dynamic")
    files = db.relationship("File", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    images = db.relationship("Image", backref="author", lazy="dynamic")

    @property
    def is_deleted(self) -> bool:
        return self.del_dt is not None

    @property
    def can_edit_posts(self) -> bool:
        return self._permission_level >= Permissions.MODERATOR

    @property
    def permissions(self) -> int:
        return self._permission_level

    @permissions.setter
    def permissions(self, value: Permissions) -> NoReturn:
        if not isinstance(value, Permissions):
            raise ValueError("Unknown permission level: %s", value)
        self._permission_level = value.value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> NoReturn:
        self._email = value.strip().lower()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> NoReturn:
        self._phone = value.strip().lower()

    @property
    def city(self) -> str:
        return self._city

    @city.setter
    def city(self, value: str) -> NoReturn:
        self._city = value.strip() or None

    @property
    def verification_token(self) -> str:
        """ Generate verification token for general proposes. """
        return jwt.encode(
            {
                'verification': self.id,
                'exp': time() + current_app.config['TOKEN_TTL']
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        ).decode("utf-8")

    @staticmethod
    def verify_token(token: bytes) -> object or NoReturn:
        """ Check verification token is correct for current user. """
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['verification']
            return User.query.get(user_id)
        except BaseException as exc:
            current_app.logger.debug("Invalid token:\n%s", exc)

    def set_password(self, value: str) -> NoReturn:
        self._password_hash = generate_password_hash(value)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self._password_hash, password)

    def delete(self, reason: str) -> NoReturn:
        self.del_reason = reason.strip().lower()
        self.del_dt = datetime.utcnow()

    def avatar(self, size: int) -> str:
        return get_gravatar_url(self._email, size=size)

    def __repr__(self) -> str:
        return f"<User[{self.id}]: {self.email}, {self.phone}, {self.name}>"


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """ Get current user from db if it's exists. """
    return User.query.get(int(user_id))


MODELS = (Comment, File, Image, Post, User)
