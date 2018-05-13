from threading import Thread

from flask import current_app
from flask_mail import Message

from web_client import mail


def send_email(subject: str,
               sender: str,
               recipients: list or tuple,
               text_body: str,
               html_body: str=None,
               attachments: list=None,
               sync: bool=False) -> None:
    """
        Send email from app.

        :param attachments: [(filename, media_type, attached_file), ...]
    """

    def send_async_email(app: object, msg: str) -> None:
        """ Send mail from app context. """
        with app.app_context():
            mail.send(msg)

    current_app.logger.info("send email '%s' to %s", subject, recipients)
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body if html_body else text_body

    if attachments is not None:
        current_app.logger.debug("email to %s has attachments", recipients)
        for attachment in attachments:
            msg.attach(*attachment)

    if sync:
        mail.send(msg)
    else:
        Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        ).start()
