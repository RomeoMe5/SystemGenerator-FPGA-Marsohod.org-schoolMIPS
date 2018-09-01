import os


try:
    from configs.engine import LOGGER
except ImportError as exc:
    import logging as LOGGER
    LOGGER.debug(exc)


# static class
class PATHS:
    ROOT = os.path.dirname(os.path.dirname(__file__))
    BASE = os.path.abspath(os.path.dirname(ROOT))
    STATIC = os.path.join(ROOT, "static")
    TEMPL = os.path.join(ROOT, "templates")
