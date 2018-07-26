from typing import NoReturn

from flask import current_app
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

from web_client.models import User
from web_client.utils import VALID_EMAIL_DOMAIN


class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign In"))


# password should be set manually
class RegistrationForm(FlaskForm):
    email = StringField(
        _l("Email"),
        validators=[DataRequired(), Email()],
        description=_l("Supported email providers: mail, yandex, gmail, "
                       "rambler, outlook")
    )
    submit = SubmitField(_l("Register"))

    def validate_email(self, email: StringField) -> NoReturn:
        email = email.data.strip().lower()
        if VALID_EMAIL_DOMAIN.search(email) is None:
            current_app.logger.debug("[auth] invalid domain: %s", email)
            raise ValidationError(_l("Unsupported email domain"))
        user = User.query.filter_by(is_deleted=False, _email=email).first()
        if user is not None:
            current_app.logger.debug("[auth] existing email: %s", email)
            raise ValidationError(_l("Please, use a different email address"))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        _l("Email"),
        validators=[DataRequired(), Email()],
        description=_l("Provide email address you have registered")
    )
    submit = SubmitField(_l("Request Password Reset"))


class SetPasswordForm(FlaskForm):
    password = PasswordField(
        _l("Password"),
        validators=[DataRequired(), Length(min=7, max=50)],
        description=_l("Please, choose complex passwords for secure reasons")
    )
    password2 = PasswordField(
        _l("Repeat Password"),
        validators=[DataRequired(), EqualTo("password")],
        description=_l("Repeat password")
    )
    submit = SubmitField(_l("Update Password"))
