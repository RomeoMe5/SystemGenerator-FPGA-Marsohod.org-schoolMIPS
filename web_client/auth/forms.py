from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import (BooleanField, IntegerField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign In"))


# password should be set manually
class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    city = StringField(_("City"))
    company = StringField(_("Company"), validators=[DataRequired()])
    position = StringField(_("Position"), validators=[DataRequired()])
    age = IntegerField(_("Age"), validators=[DataRequired()])
    submit = SubmitField(_l("Register"))

    def validate_age(self, age: int) -> None:
        if age < 8 or age > 110:
            raise ValidationError(_l("Please enter your actual age."))

    def validate_email(self, email: str) -> None:
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l("Please use a different email address."))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))


class SetPasswordForm(FlaskForm):
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(_l("Repeat Password"), validators=[
        DataRequired(), EqualTo("password")
    ])
    submit = SubmitField(_l("Request Password Reset"))
