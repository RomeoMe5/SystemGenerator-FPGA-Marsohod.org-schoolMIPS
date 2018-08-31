""" Rendering interface """

import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Environment, Template

from engine.utils import PATHS
from engine.utils.log import LOGGER, log
from engine.utils.misc import none_safe

try:
    from configs.engine import COPYRIGHT
except ImportError as exc:
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
        def wrapper(*args, **kwargs) -> Any:
            f_type = file_type  # because of naming scope conflicts
            if not f_type:
                f_type = path.split()[0]
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
            quartus_version: str,
            meta_info: dict=None,
            revisions: dict=None,
            **kwargs) -> str:
        """ Template rendering interface for .qpf files """
        meta_info = meta_info or {}
        meta_info.update({
            'date': Render.format_date(quoted=False, sep=True),
            'quartus_version': quartus_version
        })
        revisions = revisions or {}
        revisions.update({'project_revision': project_name})
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
            original_quartus_version: str="9.0",
            last_quartus_version: str="9.0",
            project_output_directory: str=None,
            user_assignments: dict=None,
            global_assignments: dict=None,
            **kwargs) -> str:
        """ Template rendering interface for .qsf files """
        global_assignments = global_assignments or {}
        project_output_directory = project_output_directory or "project_output"
        global_assignments.update({
            'project_creation_time_date': Render.format_date().upper(),
            'family': f"\"{family}\"",
            'device': device,
            'original_quartus_version': f"\"{original_quartus_version}\"",
            'last_quartus_version': f"\"{last_quartus_version}\"",
            'top_level_entity': f"\"{project_name}\"",
            'project_output_directory': project_output_directory,
            # [feature] [minor] TODO 'sdc_file': f"{project_name}.sdc"
        })
        return Render._render(
            project_name=project_name,
            global_assignments=global_assignments,
            user_assignments=user_assignments,
            **kwargs
        )

    # [bug] TODO: fix bug in template rendering instead of using regexes
    # [feature] TODO: add correct sdc generation
    @staticmethod
    @load_template("sdc.jinja")
    def sdc(project_name: str, **kwargs) -> str:
        """ Template rendering interface for .sdc files """
        import re  # to fix comments rendering

        rendered = Render._render(project_name=project_name, **kwargs)
        rendered = re.sub(r"(?m)^#\s?\n", "\n# ", rendered)
        return rendered

    @staticmethod
    @load_template("v.jinja")
    def v(project_name: str,
          assignments: dict=None,
          wires: dict=None,
          structures: dict=None,
          **kwargs) -> str:
        """ Template rendering interface for .v files """

        print("assign = ", assignments)
        print("wire = ", wires)
        print("struct = ", structures)
        print("=" * 100)
        return Render._render(
            project_name=project_name,
            assignments=assignments,
            wires=wires,
            structures=structures,
            ** kwargs
        )

    @staticmethod
    def functions(name: str,
                  clock_rate: int=100000000,  # eq to clock_freq
                  clock_freq: int=None,
                  delay: int=100,  # debouncer (millis)
                  width: int=2,  # dmx
                  out_freq: int=1000000,  # generator
                  baud_rate: int=9600,  # uart
                  **kwargs) -> str:
        """ Template rendering interface for additional functions """
        path = f"functions/{name}"
        return none_safe()(Render._render)(
            template=ENV.get_template(path),
            clock_rate=clock_rate or clock_freq,
            clock_freq=clock_rate or clock_freq,
            delay=delay,
            width=width,
            out_freq=out_freq,
            baud_rate=baud_rate,
            **kwargs
        )
