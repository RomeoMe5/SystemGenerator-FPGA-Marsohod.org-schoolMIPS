import os
from random import randint, seed
from typing import NoReturn

import forgery_py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from configs.web_client import Config
from tests import logging
from web_client import create_app, db
from web_client.models import BackupableMixin, Comment, Post, Role, User


MOCK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock")
mock_db = SQLAlchemy()


def commit_or_rollback(db: SQLAlchemy) -> NoReturn:
    try:
        db.session.commit()
    except BaseException as exc:
        db.session.rollback()
        raise exc


def create_mock_app(db: SQLAlchemy, name: str="test") -> Flask:
    return create_app(config_name="test", db=db, name=name)


class MockModel(BackupableMixin, mock_db.Model):
    __tablename__ = "mockmodel"
    id = mock_db.Column(mock_db.Integer, primary_key=True)

    data = mock_db.Column(mock_db.String(16))


class MockGenerator(object):
    @staticmethod
    def comments(count: int) -> int:
        seed()
        added_count = 0
        users_count = User.query.count()
        posts_count = Post.query.count()
        for idx in range(count):
            user = User.query.offset(randint(0, users_count - 1)).first()
            post = Post.query.offset(randint(0, posts_count - 1)).first()
            comment = Comment()
            comment.text = forgery_py.lorem_ipsum.sentences(randint(1, 5))
            comment.author = user
            comment.post = post
            db.session.add(comment)
            try:
                db.session.commit()
                added_count += 1
            except IntegrityError as exc:
                logging.debug(exc)
                db.session.rollback()
        return added_count

    # [future] TODO finish generation
    @staticmethod
    def files(count: int) -> int:
        pass

    # [future] TODO finish generation
    @staticmethod
    def images(count: int) -> int:
        pass

    @staticmethod
    def posts(count: int) -> int:
        seed()
        added_count = 0
        users_count = User.query.count()
        for idx in range(count):
            user = User.query.offset(randint(0, users_count - 1)).first()
            post = Post()
            post.text = forgery_py.lorem_ipsum.sentences(randint(1, 5))
            post.title = forgery_py.lorem_ipsum.sentence()
            post.author = user
            post.visible = randint(1, 100) == 1
            post.create_dt = forgery_py.date.date(past=True)
            db.session.add(post)
            try:
                db.session.commit()
                added_count += 1
            except IntegrityError as exc:
                logging.debug(exc)
                db.session.rollback()
        return added_count

    @staticmethod
    def roles(count: int) -> int:
        seed()
        added_count = 0
        for idx in range(count):
            role = Role()
            role.name = forgery_py.lorem_ipsum.word()
            role.default = idx == 0
            db.session.add(role)
            try:
                db.session.commit()
                added_count += 1
            except IntegrityError as exc:
                logging.debug(exc)
                db.session.rollback()
        return added_count

    @staticmethod
    def users(count: int) -> int:
        seed()
        added_count = 0
        roles_count = Role.query.count()
        for idx in range(count):
            role = Role.query.offset(randint(0, roles_count - 1)).first()
            user = User()
            user.email = forgery_py.internet.email_address()
            user.role = role
            user.set_password(forgery_py.lorem_ipsum.word())
            user.reg_dt = forgery_py.date.date(past=True)
            user.last_seen = forgery_py.date.date(past=True)
            user.city = forgery_py.address.city()
            user.name = forgery_py.internet.user_name()
            db.session.add(user)
            try:
                db.session.commit()
                added_count += 1
            except IntegrityError as exc:
                logging.debug(exc)
                db.session.rollback()
        return added_count
