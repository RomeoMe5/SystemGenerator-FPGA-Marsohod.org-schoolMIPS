import string
from hashlib import md5
from random import SystemRandom
from urllib import parse


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


def get_random_str(n: int=25) -> str:
    """ Generate random string with len == n. """
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(SystemRandom().choice(alphabet) for _ in range(n))
