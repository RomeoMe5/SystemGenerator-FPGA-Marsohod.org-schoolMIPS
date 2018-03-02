""" Rendering interface """

import os
from collections import Callable
from datetime import datetime
from functools import wraps

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Environment, Template

from configs.engine import COPYRIGHT
from engine.utils import PATHS
from engine.utils.log import LOGGER, log

ENV = Environment(
    loader=FileSystemLoader(PATHS['templ'], encoding="utf-8"),
    autoescape=select_autoescape(enabled_extensions=(), default=False),
    trim_blocks=True,
    lstrip_blocks=True,
    newline_sequence="\n",
    keep_trailing_newline=True,
    auto_reload=False
)


def load_template(path: str, file_type: str=None) -> Callable:
    """
        Load template and pass it as named argument 'template' to function

        Doesn't handle exceptions.
    """
    def decor(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> object:
            f_type = file_type  # because of naming scope conflicts
            if not f_type:
                f_type = path.split()[0]  # func.__name__
                LOGGER.debug("Assume file type is '%s'.", f_type)
            LOGGER.debug("Loading template '%s'...", path)
            return func(
                *args,
                template=ENV.get_template(path),
                file_type=func.__name__,
                **kwargs
            )
        return wrapper
    return decor


class Render(object):
    """ Collection of renders for templates """

    @staticmethod
    @log
    def _render(template: Template, **kwargs) -> str:
        LOGGER.debug("Rendering '%s' template...", template.filename)
        return "\n".join(template.generate(
            company_name=kwargs.pop('copyright', COPYRIGHT),
            **kwargs
        ))

    @staticmethod
    @load_template("qpf.jinja")
    def qpf(meta_info: dict=None,
            revisions: dict=None,
            **kwargs) -> str:
        """ Template rendering interface for .qpf files """
        if not meta_info:
            meta_info = {}
        meta_info['date'] = str(datetime.utcnow())
        return Render._render(
            meta_info=meta_info,
            revisions=revisions,
            **kwargs
        )

    @staticmethod
    @load_template("qsf.jinja")
    def qsf(global_assignments: dict=None,
            user_assignments: dict=None,
            **kwargs) -> str:
        """ Template rendering interface for .qsf files """
        return Render._render(
            global_assignments=global_assignments,
            user_assignments=user_assignments,
            **kwargs
        )

    # TODO: not useful?
    @staticmethod
    @load_template("sdc.jinja")
    def sdc(**kwargs) -> str:
        """ Template rendering interface for .sdc files """
        return Render._render(**kwargs)

    @staticmethod
    @load_template("v.jinja")
    def v(project_name: str, **kwargs) -> str:
        """ Template rendering interface for .v files """
        return Render._render(project_name=project_name, **kwargs)
