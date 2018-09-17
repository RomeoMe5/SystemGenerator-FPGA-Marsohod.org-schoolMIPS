from datetime import datetime
from time import sleep
from typing import NoReturn

import pytest

from tests import logging
from tests.web_client import commit_or_rollback, create_mock_app
from web_client import PATHS, db
from web_client.models import (DEFAULT_ROLE, EDITED_TIMEOUT, ROLES, Comment,
                               File, Image, Permission, Post, Role, User)


class TestModels(object):
    def setup_class(self) -> NoReturn:
        self.app = create_mock_app(db=db)
        self.app.app_context().push()
        db.create_all()

    def teardown_class(self) -> NoReturn:
        db.session.remove()
        db.drop_all()
        # self.app.app_context().pop()

    def test_Comment(self) -> NoReturn:
        text = "# Some comment text."
        comment = Comment()
        logging.debug(comment)
        comment.text = text
        db.session.add(comment)
        commit_or_rollback(db)
        assert isinstance(comment.id, int)
        assert isinstance(comment.create_dt, datetime)
        assert comment.text == text
        assert isinstance(comment.html, str)
        assert comment.html != text
        assert Comment.query.count()
        sleep(EDITED_TIMEOUT)
        comment.text = text
        assert not comment.is_edited
        comment.text = text + "123"
        assert comment.is_edited
        db.session.delete(comment)
        commit_or_rollback(db)
        assert not Comment.query.count()

    def test_File(self) -> NoReturn:
        name = "file"
        file = File()
        logging.debug(file)
        file.name = name
        db.session.add(file)
        commit_or_rollback(db)
        assert isinstance(file.id, int)
        assert file.name == name
        assert isinstance(file.path, str)
        assert isinstance(file.uri, str)
        assert PATHS.FILES in file.path
        assert isinstance(file.create_dt, datetime)
        assert file.is_dir is False
        assert isinstance(file.load_count, int)
        assert File.query.count()
        db.session.delete(file)
        commit_or_rollback(db)
        assert not File.query.count()

    def test_Image(self) -> NoReturn:
        fmt = "png"
        name = ".".join(("test-image", fmt))
        image = Image()
        logging.debug(image)
        image.name = name
        db.session.add(image)
        commit_or_rollback(db)
        assert isinstance(image.id, int)
        assert image.name == name
        assert image.fmt == fmt
        assert isinstance(image.uri, str)
        assert isinstance(image.create_dt, datetime)
        assert image.load_count == 0
        assert image.link == image.uri
        assert image.load_count == 1
        assert Image.query.count()
        db.session.delete(image)
        commit_or_rollback(db)
        assert not Image.query.count()

    def test_Post(self) -> NoReturn:
        title = "TEST Post"
        text = "# Some post text."
        post = Post()
        logging.debug(post)
        post.title = title
        post.text = text
        db.session.add(post)
        commit_or_rollback(db)
        assert isinstance(post.id, int)
        assert post.text == text
        assert isinstance(post.html, str)
        assert post.html != text
        assert isinstance(post.create_dt, datetime)
        assert isinstance(post.uri, str)
        assert post.title == title
        assert post.watch_count == 0
        assert post.visible is True
        assert Post.query.count()
        sleep(EDITED_TIMEOUT)
        post.text = text
        post.title = title
        assert not post.is_edited
        post.text = text + "123"
        assert post.is_edited
        post.edited_dt = None
        assert not post.is_edited
        uri = post.uri
        post.title = title + "123"
        assert post.is_edited
        assert post.uri == uri
        db.session.delete(post)
        assert not Post.query.count()

    def test_Role(self) -> NoReturn:
        name = "user"
        role = Role()
        logging.debug(role)
        role.name = name
        db.session.add(role)
        commit_or_rollback(db)
        assert isinstance(role.id, int)
        assert role.name == name
        assert role.default is False
        assert isinstance(role.permissions, int)
        assert Role.query.count()
        db.session.delete(role)
        assert not Role.query.count()

    def test_Role_insert_roles(self) -> NoReturn:
        Role.insert_roles()
        for role_name, permissions in ROLES.items():
            role = Role.query.filter_by(_name=role_name).first()
            assert role is not None
            for permission in permissions:
                assert role.has_permission(permission)
            if role.name == DEFAULT_ROLE:
                assert role.default
            db.session.delete(role)
        db.session.commit()

    def test_User(self) -> NoReturn:
        email = "test@mail.com"
        password = "pass123"
        user = User()
        logging.debug(user)
        user.email = email
        user.set_password(password)
        db.session.add(user)
        commit_or_rollback(db)
        assert isinstance(user.id, int)
        assert user.email == email
        assert user.check_password(password)
        assert isinstance(user.reg_dt, datetime)
        # assert user.role is not None  # Role model is empty
        assert User.query.count()
        token = user.get_verification_token(expires_in=5)
        assert User.verify_token(token) is user
        db.session.delete(user)
        commit_or_rollback(db)
        assert not User.query.count()


# [minor] TODO database shouldn't be dropped on each test case
class TestModelsConnections(object):
    def setup_class(self) -> NoReturn:
        self.app = create_mock_app(db=db)
        self.app.app_context().push()

    def setup_method(self) -> NoReturn:
        db.create_all()
        text = "# Some text."
        self.comment = Comment()
        self.comment.text = text
        self.file = File()
        self.file.name = "file"
        self.image = Image()
        self.image.name = "test-name.png"
        self.post = Post()
        self.post.title = "TEST Post"
        self.post.text = text
        self.role = Role()
        self.role.name = "user"
        self.user = User()
        self.user.email = "test@mail.com"
        self.user.set_password("pass123")

    def teardown_method(self) -> NoReturn:
        db.session.remove()
        db.drop_all()

    def teardown_class(self) -> NoReturn:
        pass  # self.app.app_context().pop()

    @staticmethod
    def simple_check(*items) -> NoReturn:
        for item in items:
            db.session.add(item)
        commit_or_rollback(db)
        for item in items:
            assert item is item.__class__.query.first()

        for item in items:
            db.session.delete(item)
        commit_or_rollback(db)
        for item in items:
            assert not item.__class__.query.count()

    def test_Comment(self) -> NoReturn:
        self.comment.author = self.user
        self.comment.post = self.post
        self.simple_check(self.comment, self.user, self.post)

    def test_File(self) -> NoReturn:
        self.file.author = self.user
        self.file.files.append(self.file)
        self.simple_check(self.file, self.user)

    def test_Image(self) -> NoReturn:
        self.image.author = self.user
        self.simple_check(self.image, self.user)

    def test_Post(self) -> NoReturn:
        self.post.author = self.user
        self.post.comments.append(self.comment)
        self.simple_check(self.post, self.user, self.comment)

    def test_Post_delete_comments(self) -> NoReturn:
        db.session.add(self.post)
        for comment in [Comment(_text="abc") for _ in range(10)]:
            db.session.add(comment)
            self.post.comments.append(comment)
        db.session.commit()
        assert Post.query.count()
        assert Comment.query.count() == 10
        db.session.delete(self.post)
        db.session.commit()
        assert not Post.query.count()
        assert not Comment.query.count()

    def test_Role(self) -> NoReturn:
        self.role.users.append(self.user)
        self.simple_check(self.role, self.user)

    def test_User(self) -> NoReturn:
        self.user.posts.append(self.post)
        # self.user.files = self.file
        self.user.comments.append(self.comment)
        self.user.images.append(self.image)
        self.user.role = self.role
        self.simple_check(self.user, self.image, self.post, self.comment,
                          self.role)
