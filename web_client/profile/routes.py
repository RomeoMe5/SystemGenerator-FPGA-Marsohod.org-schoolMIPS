from datetime import datetime
from typing import NoReturn

from flask import (current_app, flash, redirect, render_template, request,
                   url_for)
from flask_babel import _
from flask_login import current_user, login_required, logout_user

from web_client import db
from web_client.models import Post, User
from web_client.profile import bp
from web_client.profile.forms import DeleteProfileForm, EditProfileForm


@bp.before_request
def before_request() -> NoReturn:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route("/<username>")
@login_required
def user(username: str) -> object:
    user = User.query.filter_by(is_deleted=False,
                                _username=username).first_or_404()
    posts = (user.posts
             .filter_by(visible=True)
             .order_by(Post.create_dt.desc())
             .paginate(
                 request.args.get("page", 1, type=int),
                 current_app.config['POSTS_PER_PAGE'],
                 True  # enable 404 error
             ))

    next_page_url = None
    if posts.has_next:
        next_page_url = url_for("profile.user", username=user.username,
                                page=posts.next_num)
    prev_page_url = None
    if posts.has_prev:
        prev_page_url = url_for("profile.user", username=user.username,
                                page=posts.prev_num)

    return render_template(
        "profile/user.html",
        user=user,
        posts=posts.items,
        next_page_url=next_page_url,
        prev_page_url=prev_page_url
    )


@bp.route("/<username>/popup")
@login_required
def user_popup(username: str) -> object:
    user = User.query.filter_by(
        is_deleted=False,
        _username=username.strip().lower()
    ).first_or_404()
    return render_template("profile/user_popup.html", user=user)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit() -> object:
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_app.logger.info("Edit user %s", current_user)
        current_user.username = form.username.data
        current_user.university = form.university.data
        current_user.city = form.city.data
        current_user.course = form.course.data
        current_user.faculty = form.faculty.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("profile.user",
                                username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.university.data = current_user.university
        form.city.data = current_user.city
        form.course.data = current_user.course
        form.faculty.data = current_user.faculty

    return render_template(
        "profile/edit.html",
        title=_("Edit Profile"),
        form=form
    )


@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete() -> object:
    form = DeleteProfileForm()
    if form.validate_on_submit():
        current_app.logger.info("Delete user: %s", user)
        current_user.del_reason = form.reason.data
        current_user.delete()
        db.session.commit()

        current_app.logger.info("Logout deleted user: %s", current_user)
        logout_user()
        return redirect(url_for("main.index"))

    return render_template(
        "profile/delete.html",
        title=_("Deactivate account"),
        form=form
    )
