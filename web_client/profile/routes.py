from datetime import datetime
from typing import NoReturn

from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_babel import _
from flask_login import current_user, login_required, logout_user

from web_client import db
from web_client.models import Post, Role, User
from web_client.profile import bp
from web_client.profile.forms import (DeleteProfileForm, EditProfileAdminForm,
                                      EditProfileForm)


@bp.before_request
def before_request() -> NoReturn:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route("/<int:uid>")
@login_required
def user(uid: int) -> object:
    user = User.query.get_or_404(uid)
    if user.is_deleted:
        return abort(404)

    posts = (user.posts
             .filter_by(visible=True)
             .order_by(Post.create_dt.desc())
             .paginate(
                 request.args.get("page", 1, type=int),
                 current_app.config['ITEMS_PER_PAGE'],
                 True  # enable 404 error
             ))

    next_page = None if not posts.has_next else \
        url_for("profile.user", uid=user.id, page=posts.next_num)
    prev_page = None if not posts.has_prev else \
        url_for("profile.user", uid=user.id, page=posts.prev_num)

    return render_template(
        "profile/user.html",
        user=user,
        posts=posts.items,
        next_page_url=next_page,
        prev_page_url=prev_page
    )


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit() -> object:
    form = EditProfileForm()
    if form.validate_on_submit():
        current_app.logger.info("Edit user %s", current_user)
        current_user.name = form.name.data
        current_user.city = form.city.data
        current_user.university = form.university.data
        current_user.faculty = form.faculty.data
        current_user.course = form.course.data
        db.session.add(current_user)
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("profile.user", uid=current_user.id))
    elif request.method == "GET":
        form.name.data = current_user.name
        form.city.data = current_user.city
        form.university.data = current_user.university
        form.faculty.data = current_user.faculty
        form.course.data = current_user.course

    return render_template(
        "profile/edit.html",
        title=_("Edit Profile"),
        form=form
    )


@bp.route("/edit/<int:uid>", methods=["GET", "POST"])
@login_required
def edit_admin(uid: int) -> object:
    user = User.query.get_or_404(uid)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        current_app.logger.info("Edit user %s as admin", user)
        user.email = form.email.data
        user.role = Role.query.get(form.role.data)
        if not user.is_deleted and form.is_deleted.data:
            user.del_reason = f"[removed by {current_user}]"
        user.is_deleted = form.is_deleted.data
        user.name = form.name.data
        user.city = form.city.data
        user.university = form.university.data
        user.faculty = form.faculty.data
        user.course = form.course.data
        db.session.add(user)
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("profile.user", uid=user.id))
    elif request.method == "GET":
        form.email.data = user.email
        form.role.data = user.role_id
        form.is_deleted.data = user.is_deleted
        form.name.data = user.name
        form.city.data = user.city
        form.university.data = user.university
        form.faculty.data = user.faculty
        form.course.data = user.course

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
        db.session.add(current_user)
        db.session.commit()

        current_app.logger.info("Logout deleted user: %s", current_user)
        logout_user()
        return redirect(url_for("profile.user", uid=current_user.id))

    return render_template(
        "profile/delete.html",
        title=_("Deactivate account"),
        form=form
    )
