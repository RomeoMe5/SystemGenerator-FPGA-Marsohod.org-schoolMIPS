from flask import current_app, render_template
from flask_babel import _

from web_client.models import User
from web_client.utils.misc import send_email


def send_password_update_email(user: User,
                               expires_in: float or int=86400) -> None:
    token = user.get_verification_token(expires_in=expires_in)
    current_app.logger.info("Send mail to %s: token=%s", user, token)
    send_email(
        _("[%(header)s] Update Your Password",
          header=current_app.config['APP_HEADER']),
        sender=current_app.config['MAIL_SENDER'],
        recipients=[user.email],
        text_body=render_template("email/set_password.txt",
                                  user=user, token=token),
        html_body=render_template("email/set_password.html",
                                  user=user, token=token)
    )


def send_email_update_email(user: User,
                            email: str,
                            expires_in: float or int=86400) -> None:
    token = user.get_verification_token(expires_in=expires_in, data=email)
    current_app.logger.info("Send mail to %s: token=%s", user, token)
    send_email(
        _("[%(header)s] Update Your Email",
          header=current_app.config['APP_HEADER']),
        sender=current_app.config['MAIL_SENDER'],
        recipients=[user.email],
        text_body=render_template("email/set_email.txt",
                                  user=user, token=token),
        html_body=render_template("email/set_email.html",
                                  user=user, token=token)
    )
