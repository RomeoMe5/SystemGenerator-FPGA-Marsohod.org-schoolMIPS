from flask_babel import lazy_gettext as _l
from flask_babel import _
from flask_wtf import FlaskForm
from wtforms import (BooleanField, IntegerField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

from web_client.models import User


class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign In"))


# password should be set manually
class RegistrationForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    city = StringField(_l("City"), validators=[Length(max=140)])
    company = StringField(_l("Company"), validators=[
        DataRequired(), Length(min=2, max=140)
    ])
    position = StringField(_l("Position"), validators=[
        DataRequired(), Length(min=3, max=140)
    ])
    age = IntegerField(_l("Age"), validators=[DataRequired()])
    submit = SubmitField(_l("Register"))

    def validate_age(self, age: IntegerField) -> None:
        age = int(age.data)
        if age < 8 or age > 110:
            raise ValidationError(_l("Please enter your actual age."))

    def validate_email(self, email: StringField) -> None:
        user = User.query.filter_by(_email=email.data).first()
        if user is not None:
            raise ValidationError(_l("Please use a different email address."))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))


class SetPasswordForm(FlaskForm):
    password = PasswordField(_l("Password"), validators=[
        DataRequired(), Length(min=7, max=100)
    ])
    password2 = PasswordField(_l("Repeat Password"), validators=[
        DataRequired(), EqualTo("password")
    ])
    submit = SubmitField(_l("Update Password"))
