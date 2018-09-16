import os
import shutil
from datetime import datetime
from enum import Enum
from hashlib import md5
from time import time
from typing import Any, Dict, Iterable, NoReturn

import bleach
import jwt
import markdown as md
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
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


class Permission(Enum):
    NONE = 0b000000
    READ = 0b000001
    COMMENT = 0b000010
    WRITE = 0b000100
    ADD_FILES = 0b001000
    ADD_CONFIGS = 0b010000
    MODERATE = 0b100000


ROLES = {
    'user': (Permission.READ, Permission.COMMENT),
    'moderator': (Permission.READ, Permission.COMMENT,
                  Permission.WRITE, Permission.ADD_CONFIGS),
    'admin': (Permission.READ, Permission.COMMENT, Permission.WRITE,
              Permission.ADD_FILES, Permission.ADD_CONFIGS,
              Permission.MODERATE)
}
DEFAULT_ROLE = "user"

file_dirs = db.Table(
    "file_dirs",
    db.Model.metadata,
    db.Column("file_id", db.Integer, db.ForeignKey("file.id")),  # left
    db.Column("dir_id", db.Integer, db.ForeignKey("file.id"))  # right
)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission: Permission) -> bool:
        return False

    def is_administrator(self) -> bool:
        return False


class Comment(BackupableMixin, db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)

    _text = db.Column(db.Text, nullable=False)
    _text_html = db.Column(db.Text, nullable=False)
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
        return self._text

    @property
    def html(self) -> str:
        return self._text_html

    @text.setter
    def text(self, value: str) -> NoReturn:
        if self._text != value.strip():
            self._text = value.strip()
            setup_is_edited(self)

    @staticmethod
    def on_changed_text(target: object,
                        value: str,
                        oldvalue: str,
                        initiator: object) -> NoReturn:
        if value == oldvalue:
            return
        target._text_html = bleach.linkify(bleach.clean(
            md.markdown(value, output_format="html"),
            # allowed tags
            tags=("a", "abbr", "acronym", "b", "code", "em", "i", "strong"),
            strip=True
        ))

    def to_json(self) -> Dict[str, object]:
        payload = {
            'id': self.id,
            'post': self.post_id,
            'author': self.user_id
        }
        if self.is_deleted:
            payload['text'] = "Comment is deleted."
            payload['html'] = "<p>Comment is deleted.<p>"
            payload['timestamp'] = self.del_dt
        else:
            payload['text'] = self._text
            payload['html'] = self._text_html
            payload['timestamp'] = self.create_dt
        return payload

    @staticmethod
    def from_json(payload: Dict[str, object]) -> object or NoReturn:
        text = payload.get("text")
        if not text:
            return
        comment = Comment()
        comment.text = text
        return comment

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
        backref=db.backref("dirs", lazy="joined"),  # NOTE may be incorrect
        lazy="dynamic",
        # cascade="all, delete-orphan"
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

    _title = db.Column(db.String(140), nullable=False, index=True)
    _text = db.Column(db.Text, nullable=False)
    _text_html = db.Column(db.Text, nullable=False)
    uri = db.Column(db.String(325), nullable=False, index=True, unique=True)
    watch_count = db.Column(db.Integer, nullable=False, default=0)
    visible = db.Column(db.Boolean, nullable=False, index=True, default=True)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    edited_dt = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship(
        "Comment",
        backref="post",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

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
            "-".join(INVALID_CHARS.sub('', value.strip().lower()).split()),
            self.create_dt.strftime("%Y%m%d-%H%M%S")
        ))

    @property
    def text(self) -> str:
        return self._text

    @property
    def html(self) -> str:
        return self._text_html

    @text.setter
    def text(self, value: str) -> NoReturn:
        if self._text != value.strip():
            self._text = value.strip()
            setup_is_edited(self)

    @staticmethod
    def on_changed_text(target: object,
                        value: str,
                        oldvalue: str,
                        initiator: object) -> NoReturn:
        if value == oldvalue:
            return
        target._text_html = bleach.linkify(bleach.clean(
            md.markdown(value, output_format="html"),
            # allowed tags
            tags=("a", "abbr", "acronym", "b", "blockquote", "code", "em", "i",
                  "li", "ol", "pre", "strong", "ul", "h1", "h2", "h3", "p"),
            strip=True
        ))

    def to_json(self) -> Dict[str, object] or NoReturn:
        if self.visible:
            return {
                'uri': self.uri,
                'author': self.user_id,
                'titile': self._title,
                'text': self._text,
                'html': self._text_html,
                'timestamp': self.create_dt,
                'edited_dt': self.edited_dt,
                'watch_count': self.watch_count,
                'comments': [comment.id for comment in self.comments],
                'comments_count': self.comments.count()
            }

    @staticmethod
    def from_json(payload: Dict[str, object]) -> object or NoReturn:
        title = payload.get("title")
        text = payload.get("text")
        if not text or not title:
            return
        post = Post()
        post.text = text
        post.title = title
        return post

    def __repr__(self) -> str:
        return f"<Post[{self.id}]: {self.uri}, {self.watch_count}>"


class Role(BackupableMixin, db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)

    _name = db.Column(db.String(64), nullable=False, unique=True)
    default = db.Column(db.Boolean, nullable=False, default=False, index=True)
    permissions = db.Column(db.Integer, nullable=False, default=0)

    users = db.relationship("User", backref="role", lazy="dynamic")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> NoReturn:
        self._name = value.strip().lower()

    def add_permission(self, permission: Permission) -> NoReturn:
        if not self.has_permission(permission):
            self.permissions += permission.value

    def remove_permission(self, permission: Permission) -> NoReturn:
        if self.has_permission(permission):
            self.permissions -= permission.value

    def reset_permissions(self) -> NoReturn:
        self.permissions = Permission.NONE.value

    def has_permission(self, permission: Permission) -> bool:
        return self.permissions & permission.value == permission.value

    @staticmethod
    def insert_roles(roles: Dict[str, Iterable[Permission]] = ROLES,
                     default_role: str=DEFAULT_ROLE) -> NoReturn:
        for role_name, role_permissions in roles.items():
            role = Role.query.filter_by(name=role_name.lower()).first()
            if role is None:
                role = Role(name=role_name)
            role.reset_permissions()
            for permission in role_permissions:
                role.add_permission(permission)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<Role[{self.id}]: {self.name}, {self.permissions:b}>"


class User(UserMixin, BackupableMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    _email = db.Column(db.String(128), nullable=False, index=True, unique=True)
    _phone = db.Column(db.String(12), nullable=False, index=True, unique=True)
    _password_hash = db.Column(db.String(128), nullable=False)
    reg_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    name = db.Column(db.String(64))
    del_dt = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    avatar_hash = db.Column(db.String(32))
    _city = db.Column(db.String(64), index=True)
    del_reason = db.Column(db.String(256))
    course = db.Column(db.Integer)
    university = db.Column(db.String(128))
    faculty = db.Column(db.String(128))

    posts = db.relationship("Post", backref="author", lazy="dynamic")
    files = db.relationship("File", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    images = db.relationship("Image", backref="author", lazy="dynamic")
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

    def __init__(self, **kwargs) -> NoReturn:
        super(User, self).__init__(**kwargs)
        if self._email == current_app.config['ADMIN_EMAIL']:
            self.role = Role.query.filter_by(_name="admin").first()
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def is_deleted(self) -> bool:
        return self.del_dt is not None

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

    def verification_token(self, data: Any=None) -> str:
        """ Generate verification token for general proposes. """
        payload = {
            'id': self.id,
            'exp': time() + current_app.config['TOKEN_TTL']
        }
        if data is not None:
            payload['data'] = data
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        ).decode("utf-8")

    @staticmethod
    def verify_token(token: bytes or str) -> object or NoReturn:
        """ Check verification token is correct for current user. """
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return User.query.get(payload['id'])
        except BaseException as exc:
            current_app.logger.debug("Invalid token:\n%s", exc)

    @staticmethod
    def update_email(token: bytes or str) -> object or NoReturn:
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            user = User.query.get(payload['id'])
            if user:
                user.email = payload['data']
            return user
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
        if not self.avatar_hash:
            self.avatar_hash = md5(email.lower().encode("utf-8")).hexdigest()
        return get_gravatar_url(email_hash=self.avatar_hash, size=size)

    def can(self, permission: Permission) -> bool:
        return self.role is not None and self.role.has_permission(permission)

    def is_administrator(self) -> bool:
        return self.can(Permission.MODERATE)

    def __repr__(self) -> str:
        return f"<User[{self.id}]: {self.email}, {self.phone}, {self.name}>"


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """ Get current user from db if it's exists. """
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser

db.event.listen(Post._text, "set", Post.on_changed_text)
db.event.listen(Comment._text, "set", Comment.on_changed_text)

MODELS = (Comment, File, Image, Post, Role, User)
