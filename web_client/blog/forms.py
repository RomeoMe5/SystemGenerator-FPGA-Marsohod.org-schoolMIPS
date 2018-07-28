from typing import NoReturn

from flask import current_app
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import (BooleanField, MultipleFileField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import DataRequired, Length, ValidationError

from web_client.models import Post


class EditPostForm(FlaskForm):
    title = StringField(
        _l("Post Title"),
        validators=[DataRequired(), Length(min=10, max=140)],
        description=_l("Post title should be unique")
    )
    text = TextAreaField(
        _l("Post Text"),
        validators=[DataRequired()],
        description=_l("Post content can be formated as markdown")
    )
    visible = BooleanField(
        _l("Should this post be visible by others?"),
        default=True
    )
    submit = SubmitField(_l("Add New Post"))

    def __init__(self, original_title: str=None, *args, **kwargs) -> NoReturn:
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_title = None
        if original_title is not None:
            self.original_title = escape(original_title.strip())

    def validate_title(self, title: StringField) -> NoReturn:
        title = escape(title.data.strip())
        if title == self.original_title:
            del title
            return
        post = Post.query.filter_by(_title=title).first()
        del title
        if post is not None:
            current_app.logger.debug("Existing title: %s", post)
            del post
            raise ValidationError(_l("Please use a different title"))


class UploadImageForm(FlaskForm):
    images = MultipleFileField(
        _l("Select images to upload"),
        validators=[DataRequired()]
    )
    submit = SubmitField(_l("Upload Image"))


class EditCommentForm(FlaskForm):
    text = TextAreaField(_l("Comment Text"), validators=[DataRequired()])
    submit = SubmitField(_l("Submit"))


# [feature] TODO
class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs) -> NoReturn:
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
