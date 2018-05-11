""" Rendering interface """

import os
import re
from collections import Callable
from datetime import datetime
from functools import wraps

from engine.utils import PATHS
from engine.utils.log import LOGGER, log
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Environment, Template

try:
    # global config imports
    from configs.engine import COPYRIGHT
except ImportError as err:
    # default values
    COPYRIGHT = "Higher School for Economics University"


ENV = Environment(
    loader=FileSystemLoader(PATHS.TEMPL, encoding="utf-8"),
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
    def _render(template: Template, **kwargs) -> str:
        LOGGER.debug("Rendering '%s' template...", template.filename)
        return "\n".join(template.generate(
            company_name=kwargs.pop('copyright', COPYRIGHT),
            **kwargs
        ))

    @staticmethod
    def format_date(date_t: datetime=None,
                    quoted: bool=True,
                    sep: bool=False) -> str:
        """
            Return date in Quartus compatible format

            F.i. "12:40:01 DECEMBER 27,2017"
        """
        if date_t is None:
            date_t = datetime.utcnow()
        date_f = f"{date_t:%H:%M:%S %B %d,%Y}"
        if sep:
            date_f = f"{date_t:%H:%M:%S %B %d, %Y}"
        if quoted:
            return f"\"{date_f}\""
        return date_f

    @staticmethod
    @load_template("qpf.jinja")
    def qpf(project_name: str,
            quartus_version: str="15.1.0",
            **kwargs) -> str:
        """ Template rendering interface for .qpf files """
        meta_info = {
            'date': Render.format_date(quoted=False, sep=True),
            'quartus_version': quartus_version
        }
        meta_info.update(kwargs.pop('meta_info', {}))

        revisions = {'project_revision': project_name}
        revisions.update(kwargs.pop('revisions', {}))

        return Render._render(
            project_name=project_name,
            meta_info=meta_info,
            revisions=revisions,
            **kwargs
        )

    @staticmethod
    @load_template("qsf.jinja")
    def qsf(project_name: str,
            family: str,
            device: str,
            original_quartus_version: str='"9.0"',
            last_quartus_version: str='"9.0"',
            user_assignments: dict=None,
            **kwargs) -> str:
        """ Template rendering interface for .qsf files """
        global_assignments = {
            'project_creation_time_date': Render.format_date().upper(),
            'family': family,
            'device': device,
            'original_quartus_version': original_quartus_version,
            'last_quartus_version': last_quartus_version,
            'top_level_entity': f"\"{project_name}\"",
            # 'sdc_file': f"{project_name}.sdc"
        }
        global_assignments.update(kwargs.pop('global_assignments', {}))
        return Render._render(
            project_name=project_name,
            global_assignments=global_assignments,
            user_assignments=user_assignments,
            **kwargs
        )

    # [bug] TODO: fix bug in template rendering instead of using regexes
    @staticmethod
    @load_template("sdc.jinja")
    def sdc(project_name: str, **kwargs) -> str:
        """ Template rendering interface for .sdc files """
        rendered = Render._render(project_name=project_name, **kwargs)
        # fix comments rendering
        rendered = re.sub(r"(?m)^#\s?\n", "\n# ", rendered)
        return rendered

    @staticmethod
    @load_template("v.jinja")
    def v(project_name: str,
          assigments: dict=None,
          **kwargs) -> str:
        """ Template rendering interface for .v files """
        return Render._render(
            project_name=project_name,
            assigments=assigments,
            **kwargs
        )
