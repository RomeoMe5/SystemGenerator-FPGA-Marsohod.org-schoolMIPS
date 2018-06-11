from time import time

import jwt
from flask import current_app


def encode_to_token(data: str,
                    expires_in: float or int=60 * 60 * 24,
                    encoding: str="utf-8") -> str:
    """ Generate time-expiring token for general proposes. """
    payload = {'data': data}
    if expires_in:
        payload['exp'] = time() + expires_in
    return jwt.encode(
        payload, current_app.config['SECRET_KEY'], algorithm="HS256"
    ).decode(encoding)


def decode_token(token: str or bytes) -> object or None:
    """ Get data from token if it's correct. """
    try:
        return jwt.decode(
            token, current_app.config['SECRET_KEY'], algorithms=['HS256']
        )['data']
    except BaseException as err:
        current_app.logger.info("Invalid token:\n%s", err)
