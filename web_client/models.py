import json
from datetime import datetime
from time import time

import jwt
import redis
import rq
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from web_client import db, login_manager
from web_client.utils import get_gravatar_url


class User(UserMixin, db.Model):
    """ Represents user of the system. """

    id = db.Column(db.Integer, primary_key=True)
    _email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    _password_hash = db.Column(db.String(128))
    company = db.Column(db.String(140), index=True)
    position = db.Column(db.String(140))
    city = db.Column(db.String(140), index=True)
    age = db.Column(db.Integer, index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    notifications = db.relationship("Notification", backref="user",
                                    lazy="dynamic")
    tasks = db.relationship("Task", backref='user', lazy='dynamic')

    @property
    def email(self) -> str:
        return self._email

    @property.setter
    def email(self, email: str) -> None:
        self._email = email.strip().lower()

    @property.setter
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
                               expires_in: float or int=600,  # seconds
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

    # don't commit session! Should be done on a higher level.
    def add_notification(self, name: str, data: object) -> object:
        """ Creates new notification for current user. """
        # remove old notifications of the same type (name)
        self.notifications.filter_by(name=name).delete()
        notification = Notification(
            name=name,
            payload_json=json.dumps(data),
            user=self
        )
        db.session.add(notification)
        current_app.logger.debug("'%s' notification was added.", name)
        return notification

    # don't commit session! Should be done on a higher level.
    def launch_task(self,
                    name: str,
                    description: str,
                    *args,
                    **kwargs) -> object:
        """ Starts background task for current user. """
        rq_job = current_app.task_queue.enqueue(
            ".".join([current_app.config['REDIS_TASK_NAME'], name]),
            self.id,
            *args,
            **kwargs
        )
        task = Task(
            id=rq_job.get_id(),
            name=name,
            description=description,
            user=self
        )
        db.session.add(task)
        current_app.logger.debug("'%s' task was added to tasks queue.", name)
        return task

    def get_tasks_in_progress(self) -> list:
        """ Fetch currently running background tasks. """
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name: str) -> object:
        """ Fetch currently running background task by name. """
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def __repr__(self) -> str:
        return f"<User: {self.email}>"


class Notification(db.Model):
    """ Storage for user notifications. """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    @property
    def data(self) -> dict:
        """ Loads notification's data from json payload. """
        return json.loads(str(self.payload_json))


class Task(db.Model):
    """ Storage for running background tasks. """

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self) -> rq.job.Job or None:
        """ Try to fetch rq job for current user. """
        try:
            return rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError,
                rq.exceptions.NoSuchJobError) as err:
            current_app.logger.info("Can't fetch job '%s':\n%s", self.id, err)

    def get_progress(self) -> float or int:
        """ Returns value indicated task progress from 0% to 100%. """
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """ Get current user from db if it's exists. """
    return User.query.get(int(user_id))
