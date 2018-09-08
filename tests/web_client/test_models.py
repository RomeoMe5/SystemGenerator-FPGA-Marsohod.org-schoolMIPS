from datetime import datetime
from time import sleep
from typing import NoReturn

import pytest

from tests import logging
from tests.web_client import commit_or_rollback, create_mock_app
from web_client import db
from web_client.models import (EDITED_TIMEOUT, Comment, File, Image,
                               Permissions, Post, User)


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
        assert comment.id is not None
        assert comment.create_dt is not None
        assert comment.text != text
        assert comment.raw_text == text
        assert len(Comment.query.all())
        sleep(EDITED_TIMEOUT)
        comment.text = text
        assert not comment.is_edited
        comment.text = text + "123"
        assert comment.is_edited
        db.session.delete(comment)
        commit_or_rollback(db)
        assert not len(Comment.query.all())

    # [minor] TODO finish test as File model will be complete
    def test_File(self) -> NoReturn:
        file = File()
        logging.debug(file)

    def test_Image(self) -> NoReturn:
        fmt = "png"
        name = ".".join(("test-image", fmt))
        image = Image()
        logging.debug(image)
        image.name = name
        db.session.add(image)
        commit_or_rollback(db)
        assert image.id is not None
        assert image.name == name
        assert image.fmt == fmt
        assert image.uri is not None
        assert image.create_dt is not None
        assert image.load_count == 0
        assert image.link == image.uri
        assert image.load_count == 1
        assert len(Image.query.all())
        db.session.delete(image)
        commit_or_rollback(db)
        assert not len(Image.query.all())

    def test_Post(self) -> NoReturn:
        title = "TEST Post"
        text = "# Some post text."
        post = Post()
        logging.debug(post)
        post.title = title
        post.text = text
        db.session.add(post)
        commit_or_rollback(db)
        assert post.id is not None
        assert post.text != text
        assert post.raw_text == text
        assert post.create_dt is not None
        assert post.uri is not None
        assert post.title == title
        assert post.watch_count == 0
        assert post.visible is True
        assert len(Post.query.all())
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
        assert not len(Post.query.all())

    def test_User(self) -> NoReturn:
        email = "test@mail.com"
        phone = "77777777777"
        password = "pass123"
        user = User()
        logging.debug(user)
        user.email = email
        user.phone = phone
        user.set_password(password)
        db.session.add(user)
        commit_or_rollback(db)
        assert user.id is not None
        assert user.email == email
        assert user.phone == phone
        assert user.check_password(password)
        assert user.reg_dt is not None
        assert user.permissions == Permissions.USER.value
        assert len(User.query.all())
        assert User.verify_token(user.verification_token) is user
        db.session.delete(user)
        commit_or_rollback(db)
        assert not len(User.query.all())


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
        # self.file = File()
        self.image = Image()
        self.image.name = "test-name.png"
        self.post = Post()
        self.post.title = "TEST Post"
        self.post.text = text
        self.user = User()
        self.user.email = "test@mail.com"
        self.user.phone = "77777777777"
        self.user.set_password("pass123")

    def teardown_method(self) -> NoReturn:
        db.session.remove()
        db.drop_all()

    def teardown_class(self) -> NoReturn:
        pass  # self.app.app_context().pop()

    def simple_check(self, *items) -> NoReturn:
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

    # [minor] TODO finish test as File model will be complete
    def _test_File(self) -> NoReturn:
        raise NotImplementedError

    def test_Image(self) -> NoReturn:
        self.image.author = self.user
        self.simple_check(self.image, self.user)

    def test_Post(self) -> NoReturn:
        self.post.author = self.user
        self.post.comments.append(self.comment)
        self.simple_check(self.post, self.user, self.comment)

    def test_User(self) -> NoReturn:
        self.user.posts.append(self.post)
        # self.user.files = self.file
        self.user.comments.append(self.comment)
        self.user.images.append(self.image)
        self.simple_check(self.user, self.image, self.post, self.comment)
