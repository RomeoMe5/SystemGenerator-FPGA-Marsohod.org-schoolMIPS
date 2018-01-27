""" Logging for workflow (mainly functions) """

import logging
import traceback
from collections import Callable
from functools import wraps


class Log:
    """
        Context manager for logging some event happening

        Handling exceptions (log them).
    """

    def __init__(self,
                 case_name: str,
                 level: int=logging.DEBUG,
                 **kwargs):
        self._name = case_name
        self._level = level
        self._enter_msg = kwargs.pop("enter_msg", "ENTERING::")
        self._exit_msg = kwargs.pop("exit_msg", "EXITING::")
        self._exc_msg = kwargs.pop("exc_msg", "")
        self._silent = kwargs.pop("silent", False)

    def __enter__(self) -> object:
        """ Returns it's logger instance of self if silent """
        if self._silent:
            return self

        message = ("%s%s", self._enter_msg, self._name)
        if self._level > logging.DEBUG:
            logging.info(*message)
        else:
            logging.debug(*message)

        return self

    def __exit__(self,
                 exc_type: object=None,
                 exc_val: object=None,
                 tb: object=None) -> None:
        """ Handling exceptions (log them) """
        if exc_type is not None:
            logging.error(
                "%s\n%s%s: %s\n",
                self._exc_msg,
                "\n".join([s.strip(r"\n") for s in traceback.format_tb(tb)]),
                exc_type.__name__,
                exc_val
            )

        if self._silent:
            return

        message = ("%s%s", self._exit_msg, self._name)
        if self._level > logging.DEBUG:
            logging.info(*message)
        else:
            logging.debug(*message)


class _FuncLog(Log):
    """ Context manager for logging function calls """

    def __init__(self,
                 case_name: str,
                 level: int=logging.DEBUG):
        super(_FuncLog, self).__init__(
            case_name=case_name,
            level=level,
            enter_msg="===> ",
            exit_msg="<--- "
        )


def log(log_result: bool=True,
        log_args: bool=True,
        log_kwargs: bool=True,
        name: str=None,
        level: int=logging.DEBUG) -> Callable:
    """ Returns decorator for logging function/method behavior """
    def decor(func: Callable) -> Callable:
        func_name = name
        if not func_name:
            func_name = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs) -> object:
            with _FuncLog(func_name, level):
                if log_args:
                    for arg in args:
                        logging.debug("()::%s", arg)
                if log_kwargs:
                    for key, value in kwargs.items():
                        logging.debug(r"{}::%s=%s", key, value)

                result = func(*args, **kwargs)
                if log_result:
                    logging.debug("RETURN(%s)::%s", func_name, result)
            return result
        return wrapper
    return decor
