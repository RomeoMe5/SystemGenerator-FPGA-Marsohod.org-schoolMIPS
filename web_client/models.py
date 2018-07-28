import os
from datetime import datetime
from time import time
from typing import NoReturn

import jwt
import markdown as md
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import escape, secure_filename

from web_client import FILES_PATH, db, login_manager
from web_client.utils import (INVALID_CHARS, PERMISSIONS, get_gravatar_url,
                              get_uri)


file_dirs = db.Table(
    "file_dirs",
    db.Model.metadata,
    db.Column("file_id", db.Integer, db.ForeignKey("file.id")),  # left
    db.Column("dir_id", db.Integer, db.ForeignKey("file.id"))  # right
)


class User(UserMixin, db.Model):
    """ Represents user of the system """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    _username = db.Column(db.String(64), nullable=False, index=True,
                          unique=True)
    _email = db.Column(db.String(128), nullable=False, index=True, unique=True)
    _password_hash = db.Column(db.String(128), nullable=False)
    _permission_level = db.Column(db.Integer, nullable=False, index=True,
                                  default=PERMISSIONS.USER)
    reg_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, nullable=False, index=True,
                           default=False)

    # optional
    _avatarS = db.Column(db.String(256))  # small
    _avatar = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    del_dt = db.Column(db.DateTime)
    restore_dt = db.Column(db.DateTime)
    course = db.Column(db.Integer)
    _university = db.Column(db.String(128), index=True)
    _city = db.Column(db.String(64), index=True)
    _faculty = db.Column(db.String(128), index=True)
    _del_reason = db.Column(db.String(256))

    # relations
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    files = db.relationship("File", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    images = db.relationship("Image", backref="author", lazy="dynamic")

    @property
    def can_edit_posts(self) -> bool:
        return self._permission_level >= PERMISSIONS.MODERATOR

    @property
    def link(self) -> str:
        return url_for("profile.user", username=self._username)

    @property
    def del_reason(self) -> str:
        return self._del_reason

    @del_reason.setter
    def del_reason(self, value: str) -> NoReturn:
        if value.strip():
            self._del_reason = value.strip().lower()

    @property
    def university(self) -> str:
        return self._university

    @university.setter
    def university(self, value: str) -> NoReturn:
        if value.strip():
            self._university = value.strip()

    @property
    def city(self) -> str:
        return self._city

    @city.setter
    def city(self, value: str) -> NoReturn:
        if value.strip():
            self._city = value.strip().lower()

    @property
    def faculty(self) -> str:
        return self._faculty

    @faculty.setter
    def faculty(self, value: str) -> NoReturn:
        if value.strip():
            self._faculty = value.strip()

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> NoReturn:
        if value.strip():
            self._username = value.strip().lower()

    @property
    def email(self) -> str:
        return self._email

    # NOTE email address should be validated in forms
    @email.setter
    def email(self, value: str) -> NoReturn:
        self._email = value.strip().lower()

    # NOTE it's only needed to define setter
    @property
    def password(self) -> NoReturn:
        return

    @password.setter
    def password(self, value: str) -> NoReturn:
        """ Set's password hash for current user. """
        self._password_hash = generate_password_hash(value)

    @property
    def avatar(self) -> str:
        """ Get link to user picture (512 pixels) """
        if not self._avatar:
            self._avatar = get_gravatar_url(self._email, size=512)
        return self._avatar

    @property
    def avatar_s(self) -> str:
        """ Get link to small user picture (128 pixels) """
        if not self._avatarS:
            self._avatarS = get_gravatar_url(self._email, size=128)
        return self._avatarS

    @property
    def permissions(self) -> int:
        return self._permission_level

    @permissions.setter
    def permissions(self, value: int) -> NoReturn:
        if value not in PERMISSIONS.values:
            raise ValueError("Unknown permission level: %s", value)
        self._permission_level = value

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

    def check_password(self, password: str) -> bool:
        """ Verify password is correct for current user. """
        return check_password_hash(self._password_hash, password)

    def delete(self) -> NoReturn:
        self.is_deleted = True
        self.del_dt = datetime.utcnow()

    def restore(self) -> NoReturn:
        self.is_deleted = False
        self.restore_dt = datetime.utcnow()

    def __repr__(self) -> str:
        if self.is_deleted:
            return f"<[-]User[{self.id}]: '{self.username}' '{self.email}'>"
        return f"<User[{self.id}]: '{self.username}' '{self.email}'>"


class Post(db.Model):
    """ Represents artible post """
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)

    _title = db.Column(db.String(140), nullable=False, index=True)
    _text = db.Column(db.Text, nullable=False)
    _uri = db.Column(db.String(325), nullable=False, index=True, unique=True)
    _watch_count = db.Column(db.Integer, nullable=False, default=0)
    visible = db.Column(db.Boolean, nullable=False, index=True, default=True)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    edited_dt = db.Column(db.DateTime)

    # relations
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship("Comment", backref="post", lazy="dynamic")
    images = db.relationship("Image", backref="post", lazy="dynamic")

    @property
    def was_edited(self) -> bool:
        return self.edited_dt is not None

    @property
    def title(self) -> str:
        return self._title

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def link(self) -> str:
        return url_for("blog.view", uri=self._uri)

    @property
    def del_link(self) -> str:
        return url_for("blog.delete", uri=self._uri)

    @property
    def edit_link(self) -> str:
        return url_for("blog.edit", uri=self._uri)

    # NOTE: title should be validated in forms
    @title.setter
    def title(self, value: str) -> NoReturn:
        self._title = value.strip()
        self.was_edited()
        if self._uri:
            return
        if not self.create_dt:
            self.create_dt = datetime.utcnow()
        self._uri = "-".join((
            "-".join(INVALID_CHARS.sub(value.strip().lower(), '').split()),
            self.create_dt.strftime("%Y%m%d-%H%M%S")
        ))

    @property
    def text(self) -> str:
        return md.markdown(escape(self._text), output_format="html5")

    @property
    def raw_text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> NoReturn:
        self._text = value.strip()
        self.was_edited()

    @property
    def watches(self) -> int:
        return self._watch_count

    def watched(self) -> int:
        self._watch_count += 1
        return self._watch_count

    def delete(self) -> NoReturn:
        for comment in self.comments:
            db.session.delete(comment)
        for image in self.images:
            # [dev] TODO remove images from storage
            db.session.delete(image)

    def was_edited(self) -> NoReturn:
        if not self.create_dt:
            return
        if (datetime.utcnow() - self.create_dt).total_seconds() > 1:
            self.edited_dt = datetime.utcnow()

    def __repr__(self) -> str:
        if self.visible:
            return f"<Post[{self.id}]: <{self.watches}> {self.title}>"
        return f"<[-]Post[{self.id}]: <{self.watches}> {self.title}>"


class File(db.Model):
    """ Represents stored files """
    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)

    _name = db.Column(db.String(64), nullable=False, index=True)
    _uri = db.Column(db.String(64), nullable=False, unique=True, index=True)
    _load_count = db.Column(db.Integer, nullable=False, default=0)
    _size = db.Column(db.Integer, nullable=False)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_dir = db.Column(db.Boolean, nullable=False, index=True, default=False)

    # assotiations
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
    def link(self) -> str:
        return url_for("files.storage", uri=self._uri)

    @property
    def size(self) -> float:
        return self._size / 1024  # in bytes

    @size.setter
    def size(self, value: int) -> NoReturn:
        if value < 0:
            raise ValueError("Size should be > 0")
        self._size = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def uri(self) -> str:
        return self._uri

    @name.setter
    def name(self, value: str) -> NoReturn:
        self._name = secure_filename(os.path.basename(value))
        self._uri = get_uri(value)
        while File.query.filter_by(_uri=self._uri).first() is not None:
            self._uri = get_uri(value)

    @property
    def path(self) -> str or NoReturn:
        return os.path.join(FILES_PATH, self._uri)

    @property
    def link(self) -> str:
        return url_for("files.storage", uri=self._uri)

    @property
    def loaded(self) -> int:
        return self._load_count

    def load(self) -> int:
        self._load_count += 1
        return self._load_count

    def delete(self) -> NoReturn:
        if not self.is_dir:
            os.remove(self.path)

    def __repr__(self) -> str:
        return f"<File[{self.id}]: <{self.loaded}> {self.name} [{self.uri}]>"


class Comment(db.Model):
    """ Represents posts' comments """
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)

    _text = db.Column(db.Text, nullable=False)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    edited_dt = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    @property
    def was_edited(self) -> bool:
        return self.edited_dt is not None

    @property
    def text(self) -> str:
        return md.markdown(escape(self._text), output_format="html5")

    @property
    def raw_text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> NoReturn:
        if not self.create_dt:
            self.create_dt = datetime.utcnow()
        if (datetime.utcnow() - self.create_dt).total_seconds() > 1:
            self.edited_dt = datetime.utcnow()
        # NOTE markdown enabled
        self._text = value.strip()

    def __repr__(self) -> str:
        return f"<Comment[{self.id}]: {self.author.email} > {self.post.title}>"


class Image(db.Model):
    """ Represents posts' resources (images) """
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)

    _uri = db.Column(db.String(64), nullable=False, index=True, unique=True)
    _fmt = db.Column(db.String(16), nullable=False)
    _size = db.Column(db.Integer, nullable=False)
    _load_count = db.Column(db.Integer, nullable=False, default=0)
    create_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolution = db.Column(db.String(32))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    # [dev] TODO add url for image
    @property
    def link(self) -> str:
        self.load()
        return self.uri

    @property
    def size(self) -> float:
        return self._size / 1024  # in bytes

    @size.setter
    def size(self, value: int) -> NoReturn:
        if value < 0:
            raise ValueError("Size should be > 0")
        self._size = value

    # NOTE it's only needed to define setter
    @property
    def name(self) -> NoReturn:
        return

    @property
    def fmt(self) -> str:
        return self._fmt

    @property
    def uri(self) -> str:
        return self._uri

    @name.setter
    def name(self, value: str) -> NoReturn:
        val = value.strip().lower()
        self._fmt = val.split(".")[-1]
        uri = get_uri(value)
        while Image.query.filter_by(_uri=uri).first() is not None:
            uri = get_uri(value)
        self._uri = uri

    @property
    def loaded(self) -> int:
        return self._load_count

    def load(self) -> int:
        self._load_count += 1
        return self._load_count

    def __repr__(self) -> str:
        return (f"<Image[{self.id}]: <{self.loaded}> {self.user.email} ->"
                f" {self.post.title}>")


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """ Get current user from db if it's exists. """
    return User.query.get(int(user_id))
