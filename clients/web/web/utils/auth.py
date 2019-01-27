from typing import NoReturn

from flask import current_app, render_template
from flask_babel import _

from web_client.models import User
from web_client.utils.misc import send_email


def send_password_update_email(user: User) -> NoReturn:
    token = user.verification_token
    current_app.logger.info("Send mail with password to %s", user)
    send_email(
        _("[%(header)s] Update Your Password",
          header=current_app.config['APP_HEADER']),
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template("email/set_password.jinja",
                                  user=user, token=token, type="txt"),
        html_body=render_template("email/set_password.jinja",
                                  user=user, token=token, type="html")
    )


def send_email_verification_email(user: User) -> NoReturn:
    token = user.verification_token
    current_app.logger.info("Send mail for email verification to %s", user)
    send_email(
        _("[%(header)s] Verify Your Email Address",
          header=current_app.config['APP_HEADER']),
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template("email/verify_email.txt",
                                  user=user, token=token, type="txt"),
        html_body=render_template("email/verify_email.html",
                                  user=user, token=token, type="html")
    )
