from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from web_client.app import DB, LOGIN_M


class User(UserMixin, DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(64), index=True, unique=True)
    email = DB.Column(DB.String(120), index=True, unique=True)
    password_hash = DB.Column(DB.String(128))
    last_seen = DB.Column(DB.DateTime, default=datetime.utcnow)

    def set_email(self, email: str) -> None:
        self.email = email.lower()

    def set_username(self, username: str) -> None:
        self.username = username.lower()

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User: {self.username}>"


@LOGIN_M.user_loader
def load_user(user_id: str) -> User:
    return User.query.get(int(user_id))
