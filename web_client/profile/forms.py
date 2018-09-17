from typing import NoReturn

from flask import current_app
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, Label, SelectField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, Length, Optional, Regexp,
                                ValidationError)

from web_client.models import Role, User
from web_client.utils.misc import VALID_EMAIL_DOMAIN


class EditProfileForm(FlaskForm):
    name = StringField(_l("Name"), validators=[Length(max=64), Optional()])
    city = StringField(_l("City"), validators=[Length(max=64), Optional()])
    university = StringField(
        _l("University"),
        validators=[Length(max=128), Optional()]
    )
    faculty = StringField(
        _l("Faculty"),
        validators=[Length(max=128), Optional()]
    )
    course = SelectField(_l("Course"), validators=[Optional()], coerce=int)
    submit = SubmitField(_l("Submit"))

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.course.choices = [(idx + 1, str(idx + 1)) for idx in range(6)]


class EditProfileAdminForm(FlaskForm):
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
    role = SelectField(_l("Permissions"), coerce=int)
    is_deleted = BooleanField(_l("Is Deleted"))
    name = StringField(_l("Name"), validators=[Length(max=64), Optional()])
    city = StringField(_l("City"), validators=[Length(max=64), Optional()])
    university = StringField(
        _l("University"),
        validators=[Length(max=128), Optional()]
    )
    faculty = StringField(
        _l("Faculty"),
        validators=[Length(max=128), Optional()]
    )
    course = SelectField(_l("Course"), validators=[Optional()], coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user: User, *args, **kwargs) -> NoReturn:
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.course.choices = [(idx + 1, str(idx + 1)) for idx in range(6)]
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role._name).all()]
        self.user = user

    def validate_email(self, email: StringField) -> NoReturn:
        email = email.data.strip().lower()
        user = User.query.filter_by(_email=email).first()
        del email
        if user is not None:
            current_app.logger.debug("Existing email: %s", user.email)
            del user
            raise ValidationError(_l("Please, use a different email address"))
        del user


class DeleteProfileForm(FlaskForm):
    note = Label("note", _l("This action can't be undone. Are you sure?"))
    reason = StringField(_l("Provide the reason"))
    submit = SubmitField(_l("Deactivate account"))
