""" Rendering interface """

from datetime import datetime
from functools import wraps
from typing import Any, Callable

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Environment, Template

from engine.utils.globals import LOGGER, PATHS
from engine.utils.misc import log, none_safe


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
            if not file_type:
                LOGGER.debug("Assume file type is '%s'.", func.__name__)
            LOGGER.debug("Loading template '%s'...", path)
            return func(
                *args,
                template=ENV.get_template(path),
                file_type=file_type or func.__name__,
                **kwargs
            )
        return wrapper
    return decor


class Render(object):
    """ Collection of renders for templates """

    @staticmethod
    async def _render(template: Template, **kwargs) -> str:
        LOGGER.debug("Rendering '%s' template...", template.filename)
        return "\n".join(template.generate(**kwargs))

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
    async def qpf(project_name: str,
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
        return await Render._render(
            project_name=project_name,
            meta_info=meta_info,
            revisions=revisions,
            **kwargs
        )

    @staticmethod
    @load_template("qsf.jinja")
    async def qsf(project_name: str,
                  family: str,
                  device: str,
                  func: object=None,
                  original_quartus_version: str="9.0",
                  last_quartus_version: str="9.0",
                  project_output_directory: str=None,
                  user_assignments: dict=None,
                  global_assignments: dict=None,
                  mips: dict=None,
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
            'project_output_directory': project_output_directory,
            # [future] [minor] TODO 'sdc_file': f"{project_name}.sdc"
        })
        return await Render._render(
            project_name=project_name,
            global_assignments=global_assignments,
            user_assignments=user_assignments,
            mips=mips,
            func=func,
            ** kwargs
        )

# [minor] BUG fix bug in template rendering instead of using regexes
# [future] TODO add correct sdc generation
# [deb] BUG: fix mips sdc generation
    @staticmethod
    @load_template("sdc.jinja")
    async def sdc(project_name: str, mips: str, **kwargs) -> str:
        """ Template rendering interface for .sdc files """
        import re  # to fix comments rendering

        rendered = await Render._render(
            project_name=project_name,
            mips=mips,
            **kwargs
        )
        rendered = re.sub(r"(?m)^#\s?\n", "\n# ", rendered)
        return rendered

    @staticmethod
    @load_template("v.jinja")
    async def v(project_name: str,
                assignments: dict=None,
                wires: dict=None,
                structures: dict=None,
                **kwargs) -> str:
        """ Template rendering interface for .v files """
        return await Render._render(
            project_name=project_name,
            assignments=assignments,
            wires=wires,
            structures=structures,
            ** kwargs
        )

    @staticmethod
    async def functions(name: str,
                        clock_rate: int=100000000,  # eq to clock_freq
                        clock_freq: int=None,
                        delay: int=100,  # debouncer (millis)
                        width: int=2,  # dmx
                        out_freq: int=1000000,  # generator
                        baud_rate: int=9600,  # uart
                        fmt: str="v.jinja",
                        **kwargs) -> str:
        """ Template rendering interface for additional functions """
        name = f"{name}.{fmt}" if fmt else name
        return await none_safe()(Render._render)(
            template=ENV.get_template(f"functions/{name}"),
            clock_rate=clock_rate or clock_freq,
            clock_freq=clock_rate or clock_freq,
            delay=delay,
            width=width,
            out_freq=out_freq,
            baud_rate=baud_rate,
            **kwargs
        )
