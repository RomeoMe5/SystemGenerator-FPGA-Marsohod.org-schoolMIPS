from flask import (current_app, flash, redirect, render_template, request,
                   url_for)
from flask_babel import _
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from web_client import db
from web_client.auth import bp
from web_client.auth.email import send_password_update_email
from web_client.auth.forms import (LoginForm, RegistrationForm,
                                   ResetPasswordRequestForm, SetPasswordForm)
from web_client.models import User
from web_client.utils import get_random_str


@bp.route('/login', methods=["GET", "POST"])
def login() -> object:
    if current_user.is_authenticated:
        current_app.logger.debug("[login] authenticated: %s", current_user)
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        current_app.logger.info("login user: %s", user)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc:
            next_page = url_for("main.index")

        return redirect(next_page)

    return render_template("auth/login.html", title=_("Sign In"), form=form)


@bp.route('/logout')
def logout() -> object:
    current_app.logger.info("logout user: %s", current_user)
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route('/register', methods=["GET", "POST"])
def register() -> object:
    if current_user.is_authenticated:
        current_app.logger.debug("[register] authenticated: %s", current_user)
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():  # assume that form handle all validations
        user = User()
        user.email = form.email.data
        user.company = form.company.data
        user.position = form.position.data
        user.age = form.age.data
        user.city = form.city.data
        user.password = get_random_str()  # temporary set random password
        db.session.add(user)
        db.session.commit()
        current_app.logger.debug("register new user: %s", user)
        flash(_("Check your email address for setting password link!"))
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html",
        title=_("Register"),
        form=form
    )


@bp.route('/reset_password_request', methods=["GET", "POST"])
def reset_password_request() -> object:
    if current_user.is_authenticated:
        current_app.logger.debug("[reset] authenticated: %s", current_user)
        return redirect(url_for("main.index"))

    reset_form = ResetPasswordRequestForm()
    if reset_form.validate_on_submit():
        user = User.query.filter_by(email=reset_form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_("Check email for the instructions to reset your password"))
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_request.html",
        title=_("Reset Password"),
        form=reset_form
    )


@bp.route('/update_password/<token>', methods=["GET", "POST"])
def update_password(token: str) -> object:
    if current_user.is_authenticated:
        current_app.logger.debug("[password] authenticated: %s", current_user)
        return redirect(url_for("main.index"))

    user = User.verify_reset_password_token(token)
    if not user:
        current_app.logger.debug("token %s has expired or invalid", token)
        flash(_("Token expired or invalid."))
        return redirect(url_for("main.index"))

    form = SetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        current_app.logger.debug("user %s change password", user)
        db.session.commit()
        flash(_("Your password has been reset."))
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/update_password.html",
        title=_("Update Password"),
        form=form
    )
