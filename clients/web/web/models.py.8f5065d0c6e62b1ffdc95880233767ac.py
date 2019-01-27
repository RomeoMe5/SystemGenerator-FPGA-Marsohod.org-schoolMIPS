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
import yaml
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import escape, secure_filename

from fpga_marsohod_generator_engine.utils.prepare import Loader
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
    COMMENT = 0b000001
    WRITE = 0b000010
    ADD_FILES = 0b000100
    MODERATE = 0b100000


ROLES = {
    'user': (Permission.COMMENT,),
    'moderator': (Permission.COMMENT, Permission.WRITE, Permission.ADD_FILES),
    'admin': (Permission.COMMENT, Permission.WRITE, Permission.ADD_FILES,
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

    @property
    def is_admin(self) -> bool:
        return False


class Comment(BackupableMixin, db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)

    _text = db.Column(db.Text, nullable=False)
    html = db.Column(db.Text, nullable=False)

    create_dt = db.Column(db.DateTime, default=datetime.utcnow)
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
        target.html = bleach.linkify(bleach.clean(
            md.markdown(value, output_format="html"),
            # allowed tags
            tags=("a", "abbr", "acronym", "b", "blockquote", "code", "em", "i",
                  "li", "ol", "pre", "strong", "ul", "p", "br", "span", "hr",
                  "h4", "h5", "h6"),
            attributes={'*': ["class", "id"], 'a': ["href", "rel"]},
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
            payload['html'] = self.html
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
        return f"<Comment[{self.id}]: {self.create_dt}>"


class Config(BackupableMixin, db.Model):
    __tablename__ = "config"
    id = db.Column(db.Integer, primary_key=True)

    yml = db.Column(db.Text, nullable=False)

    editable = db.Column(db.Boolean, default=True)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @property
    def data(self) -> object:
        return yaml.load(self.yml or "")

    @data.setter
    def data(self, value: object) -> NoReturn:
        self.yml = yaml.dump(value)

    @staticmethod
    def load_from_file(filepath: str,
                       editable: bool=True,
                       **kwargs) -> NoReturn:
        config = Config()
        config.data = Loader.load(filepath, **kwargs)
        config.editable = editable
        db.session.add(config)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<Config[{self.id}]: {self.create_dt}, {self.editable}>"


class File(BackupableMixin, db.Model):
    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), nullable=False, index=True)
    uri = db.Column(db.String(64), nullable=False, unique=True, index=True)
    _path = db.Column(db.String(64), nullable=False, unique=True, index=True)

    create_dt = db.Column(db.DateTime, default=datetime.utcnow)
    is_dir = db.Column(db.Boolean, default=False)
    size = db.Column(db.Integer)  # in bytes
    load_count = db.Column(db.Integer, default=0)

    files = db.relationship(
        "File",
        secondary=file_dirs,
        primaryjoin=(file_dirs.c.file_id == id),
        secondaryjoin=(file_dirs.c.dir_id == id),
        backref=db.backref("dirs", lazy="joined"),  # NOTE may be incorrect
        lazy="dynamic"
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> NoReturn:
        if not os.path.exists(value):
            raise FileNotFoundError(f"{value} isn't exists")
        self._path = value
        self.name = secure_filename(os.path.basename(value))
        self.is_dir = os.path.isdir(self.path)
        stat = os.stat(value)
        self.size = stat.st_size
        self.create_dt = datetime.fromtimestamp(stat.st_ctime)
        if self.uri:
            return
        self.uri = get_uri(value)
        while File.query.filter_by(uri=self.uri).first() is not None:
            self.uri = get_uri(value)

    @staticmethod
    def remove_dir(items: Iterable) -> NoReturn:
        for item in items:
            if item.is_dir:
                File.remove_dir(item.files)
            else:
                db.session.delete(item)
                os.remove(item.path)

    @staticmethod
    def reindex() -> NoReturn:
        for file in File.query.all():
            if not os.path.exists(file.path):
                db.session.delete(file)
                continue
            file.is_dir = os.path.isdir(file.path)
            stat = os.stat(file.path)
            file.size = stat.st_size
            file.create_dt = datetime.fromtimestamp(stat.st_ctime)
            db.session.add(file)
        db.session.commit()

    # [future] TODO add realization
    @staticmethod
    def discover(path: str=None) -> NoReturn:
        """ Recursively add files to table """
        if not path or not os.path.exists(path):
            return
        file = File.query.filter_by(path=path).first()
        if not file.is_dir:
            return
        else:
            pass
        if os.path.isfile(path):
            pass

    def delete(self) -> NoReturn:
        if self.is_dir:
            self.remove_dir(self.files)
            shutil.rmtree(self.path)
        else:
            os.remove(self.path)
        db.session.delete(self)

    def __repr__(self) -> str:
        return f"<File[{self.id}]: {self.path}, {self.uri}, {self.load_count}>"


class Image(BackupableMixin, db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)

    _name = db.Column(db.String(128), nullable=False, index=True)
    uri = db.Column(db.String(64), nullable=False, unique=True, index=True)

    load_count = db.Column(db.Integer, default=0)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow)
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
    html = db.Column(db.Text, nullable=False)
    uri = db.Column(db.String(325), nullable=False, index=True, unique=True)

    watch_count = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, index=True, default=True)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow)
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
            "-".join(INVALID_CHARS.sub("", value.strip().lower()).split()),
            self.create_dt.strftime("%Y%m%d-%H%M%S")
        ))

    @property
    def text(self) -> str:
        return self._text

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
        target.html = bleach.linkify(bleach.clean(
            md.markdown(value, output_format="html"),
            # allowed tags
            tags=("a", "abbr", "acronym", "b", "blockquote", "code", "em", "i",
                  "li", "ol", "pre", "strong", "ul", "h1", "h2", "h3", "p",
                  "img", "video", "div", "iframe", "br", "span", "hr", "src",
                  "class", "h4", "h5", "h6"),
            attributes={
                '*': ["class", "id"],
                'a': ["href", "rel"],
                'img': ["src", "alt"]
            },
            strip=True
        ))

    def to_json(self) -> Dict[str, object] or NoReturn:
        if self.visible:
            return {
                'uri': self.uri,
                'author': self.user_id,
                'titile': self._title,
                'text': self._text,
                'html': self.html,
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

    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer, default=0)
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
    _password_hash = db.Column(db.String(128), nullable=False)

    reg_dt = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, index=True, default=False)
    name = db.Column(db.String(64))
    del_dt = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    avatar_hash = db.Column(db.String(32))
    _city = db.Column(db.String(64), index=True)
    del_reason = db.Column(db.Text)
    course = db.Column(db.Integer)
    university = db.Column(db.String(128))
    faculty = db.Column(db.String(128))

    posts = db.relationship("Post", backref="author", lazy="dynamic")
    files = db.relationship("File", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    images = db.relationship("Image", backref="author", lazy="dynamic")
    configs = db.relationship("Config", backref="author", lazy="dynamic")
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

    def __init__(self, **kwargs) -> NoReturn:
        super(User, self).__init__(**kwargs)
        if self._email == current_app.config['ADMIN_EMAIL']:
            self.role = Role.query.filter_by(_name="admin").first()
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> NoReturn:
        self._email = value.strip().lower()

    @property
    def city(self) -> str:
        return self._city

    @city.setter
    def city(self, value: str) -> NoReturn:
        self._city = value.strip() or None

    def get_verification_token(self,
                               expires_in: float=None,
                               data: Any=None) -> str:
        """ Generate verification token for general proposes. """
        payload = {
            'id': self.id,
            'exp': time() + (expires_in or current_app.config['TOKEN_TTL'])
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

    def delete(self, reason: str=None) -> NoReturn:
        self.is_deleted = True
        self.del_reason = reason.strip().lower() if reason else None
        self.del_dt = datetime.utcnow()

    def avatar(self, size: int) -> str:
        if not self.avatar_hash:
            self.avatar_hash = \
                md5(self._email.lower().encode("utf-8")).hexdigest()
        return get_gravatar_url(email_hash=self.avatar_hash, size=size)

    def can(self, permission: Permission) -> bool:
        return self.role is not None and self.role.has_permission(permission)

    @property
    def is_admin(self) -> bool:
        return self.can(Permission.MODERATE)

    def __repr__(self) -> str:
        return f"<User[{self.id}]: {self.email}, {self.name}>"


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """ Get current user from db if it's exists. """
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser

db.event.listen(Post._text, "set", Post.on_changed_text)
db.event.listen(Comment._text, "set", Comment.on_changed_text)

MODELS = (Comment, File, Image, Post, Role, User)
__all__ = tuple(model.__name__ for model in MODELS)
