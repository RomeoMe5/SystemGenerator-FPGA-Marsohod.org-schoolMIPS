import re
from typing import NoReturn

from flask import current_app
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from werkzeug.utils import escape
from wtforms import BooleanField, IntegerField, Label, StringField, SubmitField
from wtforms.validators import (DataRequired, Length, NumberRange, Optional,
                                ValidationError)

from web_client.models import User


class EditProfileForm(FlaskForm):
    username = StringField(
        _l("Username"),
        validators=[DataRequired(), Length(min=3, max=64)],
        description=_l("Should be unique")
    )
    city = StringField(_l("City"), validators=[Length(max=64), Optional()])
    university = StringField(
        _l("University"),
        validators=[Length(max=64), Optional()]
    )
    faculty = StringField(
        _l("Faculty"),
        validators=[Length(max=64), Optional()]
    )
    course = IntegerField(
        _l("Course"),
        validators=[NumberRange(min=1, max=6), Optional()]
    )
    submit = SubmitField(_l("Submit"))

    def __init__(self, original_username: str, *args, **kwargs) -> NoReturn:
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = escape(original_username)

    def validate_username(self, username: StringField) -> NoReturn:
        if re.search(r"\W", username.data.strip()) is not None:
            raise ValidationError(_l("Please, choose username without spaces"))
        username = escape(username.data.strip().lower())
        if username == self.original_username:
            del username
            return
        user = User.query.filter_by(is_deleted=False,
                                    _username=username).first()
        del username
        if user is not None:
            current_app.logger.debug("Existing email: %s", user)
            del user
            raise ValidationError(_l("Please use a different username"))


class DeleteProfileForm(FlaskForm):
    note = Label("note", _l("This action can't be undone. Are you sure?"))
    reason = StringField(
        _l("Provide the reason"),
        validators=[Length(max=128), Optional()]
    )
    submit = SubmitField(_l("Deactivate account"))
