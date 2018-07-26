import re
import string
from hashlib import md5
from random import SystemRandom
from threading import Thread
from typing import Iterable
from urllib import parse

from flask import current_app
from flask_mail import Message

from web_client import mail

INVALID_CHARS = re.compile(r'[\/:*?"><|]')
VALID_EMAIL_DOMAIN = re.compile(r"(?i)@((gmail|outlook)\.com|(mail|rambler)\."
                                r"ru|ya(ndex)?\.(ru|com|ua|kz|by))")


class PERMISSIONS(object):
    ADMIN = 1
    MODERATOR = 2
    USER = 3
    GUEST = 4

    values = {ADMIN, MODERATOR, USER, GUEST}


class FILE_TYPES(object):
    FILE = 1
    DIR = 2

    values = {
        FILE: "file",
        DIR: "folder"
    }


def get_gravatar_url(email: str,
                     size: int=80,
                     default: str="retro",
                     rating: str="g",
                     add_type: bool=False,
                     force_default: bool=False,
                     **kwargs) -> str:
    """
        Form url for gravatar image for certain email

        Sizes form 1px to 2048px; images are squared.
        Possible ratings: "g", "pg", "r", "x".
        Add type adds ".jpg" at the end of url.
        Possible params for default:
            * ulr for image;
            * "404", "mm", "identicon", "monsterid", "wavatar", "retro",
                "robohash", "blank".
        Read more: https://en.gravatar.com/site/implement/images
    """
    rating = rating.lower().strip()
    if size < 1 or size > 2048:
        raise ValueError(f"Gravatar size should be 1-2048px! [got: {size}]")
    elif rating not in {"g", "pg", "r", "x"}:
        raise ValueError(f"Unsupported gravatar rating '{rating}'!")

    base_url = kwargs.get("base_url", r"https://secure.gravatar.com/avatar/")
    email_hash = md5(email.lower().encode("utf-8")).hexdigest()
    params = {
        's': int(size),
        'd': default.lower().strip(),
        'r': rating
    }
    if force_default:
        params['f'] = "y"

    target_url = f"{base_url}{email_hash}?{parse.urlencode(params)}"
    if add_type:
        return f"{target_url}.jpg"
    return target_url


def get_random_str(n: int=25, alphabet: Iterable=None) -> str:
    """ Generate random string with len == n. """
    if alphabet is None:
        alphabet = string.ascii_uppercase + string.digits
    return ''.join(SystemRandom().choice(alphabet) for _ in range(n))


def get_uri(resource_name: str, length: int=64) -> str:
    if length - 32 < 0:
        raise ValueError("length should be >= 32")
    salt = get_random_str(length - 32)
    return md5(resource_name.encode("utf-8")).hexdigest() + salt


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
