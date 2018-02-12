from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from web_client.app import APP, DB
from web_client.app.forms import LoginForm, RegistrationForm
from web_client.app.models import User


@APP.route('/')
@APP.route('/index')
@login_required
def index() -> str:
    return render_template(
        "index.html",
        title="Home",
        user=current_user
    )


@APP.route('/login', methods=["GET", "POST"])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # @RMB: not user is not None
        if not user or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc:  # @RMB: .netloc != ''
            next_page = url_for("index")

        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)


@APP.route('/logout')
def logout() -> str:
    logout_user()
    return redirect(url_for("index"))


@APP.route('/register', methods=["GET", "POST"])
def register() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():  # assume that form handle all validations
        user = User()
        user.set_username(form.username.data)
        user.set_email(form.email.data)
        user.set_password(form.password.data)
        DB.session.add(user)
        DB.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@APP.before_request
def set_last_seen() -> None:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        DB.session.commit()
