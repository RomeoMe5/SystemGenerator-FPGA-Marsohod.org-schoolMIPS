from flask import current_app, render_template
from flask_babel import _

from web_client.utils import send_email
from web_client.models import User


def send_password_update_email(user: User,
                               expires_in: float or int=600) -> None:
    token = user.get_verification_token(expires_in=expires_in)
    current_app.logger.info("Send mail with password to %s", user)
    send_email(
        _('[HSE FPGAMarsohodCAD] Update Your Password'),
        sender=current_app.config['MAIL_ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/set_password.txt',
                                  user=user, token=token),
        html_body=render_template('email/set_password.html',
                                  user=user, token=token)
    )
