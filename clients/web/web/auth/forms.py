from typing import NoReturn

from flask import current_app
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, EqualTo, Length, Regexp,
                                ValidationError)

from web_client.models import User
from web_client.utils.misc import VALID_EMAIL_DOMAIN


class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"), default=True)
    submit = SubmitField(_l("Sign In"))


# password should be set separately
class RegistrationForm(FlaskForm):
    email = StringField(
        _l("Email"),
        validators=[
            DataRequired(),
            Regexp(regex=VALID_EMAIL_DOMAIN, message=_l("Invalid email")),
            Email(),
            Length(min=1, max=128)
        ],
        description=_l("Supported email providers: mail, yandex, gmail, "
                       "rambler, outlook")
    )
    submit = SubmitField(_l("Register"))

    def validate_email(self, email: StringField) -> NoReturn:
        email = email.data.strip().lower()
        user = User.query.filter_by(is_deleted=False, _email=email).first()
        del email
        if user is not None:
            current_app.logger.debug("Existing email: %s", user.email)
            del user
            raise ValidationError(_l("Please, use a different email address"))
        del user


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
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Passwords must match."))
        ],
        description=_l("Repeat password")
    )
    submit = SubmitField(_l("Update Password"))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        _l("Old Password"),
        validators=[DataRequired()],
        description=_l("Your old password")
    )
    password = PasswordField(
        _l("Password"),
        validators=[DataRequired(), Length(min=7, max=50)],
        description=_l("Please, choose complex passwords for secure reasons")
    )
    password2 = PasswordField(
        _l("Repeat Password"),
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Passwords must match."))
        ],
        description=_l("Repeat password")
    )
    submit = SubmitField(_l("Update Password"))


class ChangeEmailForm(FlaskForm):
    email = StringField(
        _l("New Email"),
        validators=[
            DataRequired(),
            Regexp(regex=VALID_EMAIL_DOMAIN, message=_l("Invalid email")),
            Email(),
            Length(min=1, max=128)
        ],
        description=_l("Supported email providers: mail, yandex, gmail, "
                       "rambler, outlook")
    )
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    submit = SubmitField(_l("Update Email Address"))

    def validate_email(self, email: StringField) -> NoReturn:
        email = email.data.strip().lower()
        user = User.query.filter_by(is_deleted=False, _email=email).first()
        del email
        if user is not None:
            current_app.logger.debug("Existing email: %s", user.email)
            del user
            raise ValidationError(_l("Please, use a different email address"))
        del user
