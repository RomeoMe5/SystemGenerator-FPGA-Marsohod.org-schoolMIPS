""" Rendering interface """

import logging
from typing import Iterator

from jinja2.environment import Template

from engine.utils.decorators import default_args_for_render, load_template
from engine.utils.log import log


class Render(object):
    """ Collection of renders for templates """

    @staticmethod
    @log()
    def _render(template: Template, **kwargs) -> Iterator[str]:
        logging.debug("Rendering '%s' template...", template.filename)
        return template.generate(**kwargs)

    @staticmethod
    @load_template("qpf.jinja")
    @default_args_for_render
    def qpf(meta_info: dict=None,
            revisions: dict=None,
            **kwargs) -> Iterator[str]:
        """ Template rendering interface for .qpf files """
        return Render._render(
            meta_info=meta_info,
            revisions=revisions,
            **kwargs
        )

    @staticmethod
    @load_template("qsf.jinja")
    @default_args_for_render
    def qsf(global_assignments: dict=None,
            user_assignments: dict=None,
            **kwargs) -> Iterator[str]:
        """ Template rendering interface for .qsf files """
        return Render._render(
            global_assignments=global_assignments,
            user_assignments=user_assignments,
            **kwargs
        )

    # TODO: not useful?
    @staticmethod
    @load_template("sdc.jinja")
    @default_args_for_render
    def sdc(**kwargs) -> Iterator[str]:
        """ Template rendering interface for .sdc files """
        return Render._render(**kwargs)

    @staticmethod
    @load_template("v.jinja")
    @default_args_for_render
    def v(project_name: str, **kwargs) -> Iterator[str]:
        """ Template rendering interface for .v files """
        return Render._render(project_name=project_name, **kwargs)
