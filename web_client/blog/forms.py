from typing import NoReturn

from flask_babel import lazy_gettext as _l
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import (BooleanField, MultipleFileField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import DataRequired, Length

from web_client.models import Post


class PostForm(FlaskForm):
    title = StringField(
        _l("Post Title"),
        validators=[DataRequired(), Length(min=1, max=140)]
    )
    text = PageDownField(
        _l("Article Text"),
        validators=[DataRequired()],
        description=_l("Post content can be formated as markdown")
    )
    visible = BooleanField(
        _l("Should this post be visible by others?"),
        default=True
    )
    submit = SubmitField(_l("Submit"))


class CommentForm(FlaskForm):
    text = TextAreaField(_l("Add Comment"), validators=[DataRequired()])
    submit = SubmitField(_l("Submit"))


class UploadImageForm(FlaskForm):
    images = MultipleFileField(
        _l("Select images to upload"),
        validators=[DataRequired()]
    )
    submit = SubmitField(_l("Upload Image"))


# [future] TODO
class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs) -> NoReturn:
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
