from functools import wraps
from typing import Callable

from flask import (current_app, flash, redirect, render_template, request,
                   url_for)
from flask_babel import _
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from web_client import db
from web_client.auth import bp
from web_client.auth.forms import (LoginForm, RegistrationForm,
                                   ResetPasswordRequestForm, SetPasswordForm)
from web_client.auth.utils import send_password_update_email
from web_client.models import User
from web_client.utils import get_random_str


def filter_authenticated(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> object:
        if current_user.is_authenticated:
            current_app.logger.debug("Already authenticated: %s", current_user)
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)
    return wrapper


def get_debug_token(user: User) -> object:
    token = user.verification_token
    current_app.logger.debug("[debug session] verification token: %s", token)
    flash("This is a debug session: mailing is not supported")
    return redirect(url_for("auth.update_password", token=token))


@bp.route("/login", methods=["GET", "POST"])
@filter_authenticated
def login() -> object:
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(is_deleted=False, _email=email).first()

        if not user or not user.check_password(form.password.data):
            msg = "Invalid password: %s"
            if not user:
                msg = "User not found: %s"
            current_app.logger.info(msg, email)
            flash(_("Invalid username or password"))
            del msg
            return redirect(url_for("auth.login"))

        current_app.logger.info("Sign in user: %s", user)
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc:
            next_page = url_for("main.index")
        return redirect(next_page)

    return render_template("auth/login.html", title=_("Sign In"), form=form)


@bp.route("/logout")
def logout() -> object:
    current_app.logger.info("Logout user: %s", current_user)
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
@filter_authenticated
def register() -> object:
    form = RegistrationForm()
    # assume that form handle all validations
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        old_user = User.query.filter_by(is_deleted=True, _email=email).first()
        if old_user is not None:
            current_app.logger.info("Remove existing user: %s", old_user)
            db.session.delete(old_user)
            db.session.commit()

        user = User()
        user.email = email
        user.password = get_random_str()  # NOTE temporary set random password

        user.username = "_".join((email.split("@")[0], get_random_str(7)))
        _user = User.query.filter_by(is_deleted=False,
                                     _username=user.username).firts()
        while _user is not None:
            user.username = "_".join((email.split("@")[0], get_random_str(7)))

        del _user, email

        current_app.logger.info("Register user with tmp password: %s", user)
        db.session.add(user)
        db.session.commit()

        if current_app.config['DEBUG']:
            return get_debug_token(user)

        try:
            send_password_update_email(user)
        except BaseException as exc:
            current_app.logger.warning("Can't send email to %s: %s", user, exc)
            current_app.logger.debug("Delete user: %s", user)
            db.session.delete(user)  # remove created user
            db.session.commit()
            current_app.logger.debug("Add old user: %s", old_user)
            db.session.add(old_user)
            db.session.commit()
            flash(_("Error occurs while mailing you, please contact support!"))
            return redirect(url_for("auth.register"))
        finally:
            del old_user

        flash(_("Check your email address for setting password link!"))
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html",
        title=_("Register"),
        form=form
    )


@bp.route("/reset", methods=["GET", "POST"])
@filter_authenticated
def reset() -> object:
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            is_deleted=False,
            _email=form.email.data.strip().lower()
        ).first()
        if user is not None:
            if current_app.config['DEBUG']:
                return get_debug_token(user)
            try:
                send_password_update_email(user)
            except BaseException as exc:
                current_app.logger.warning("Can't send email to %s: %s",
                                           user, exc)
                flash(_("Error occurs while mailing you, "
                        "please contact support!"))
                return redirect(url_for("auth.register"))
        flash(_("Check email for the instructions to reset your password"))
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset.html",
        title=_("Reset Password"),
        form=form
    )


@bp.route("/update_password/<token>", methods=["GET", "POST"])
def update_password(token: str) -> object:
    user = User.verify_token(token)
    if user is None:
        current_app.logger.debug("Token %s has expired or invalid", token)
        flash(_("Token expired or invalid."))
        return redirect(url_for("main.index"))

    form = SetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        current_app.logger.debug("User %s change password", user)
        db.session.commit()
        flash(_("Your password has been updated!"))
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/update_password.html",
        title=_("Update Password"),
        form=form
    )
