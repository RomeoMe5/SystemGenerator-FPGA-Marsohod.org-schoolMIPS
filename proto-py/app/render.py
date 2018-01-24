import os
from functools import partial
from jinja2 import Environment, FileSystemLoader

from app import ROOT_DIR
from app.utils.decorators import default_args_for_render, load_template

TEMPL_ENV = Environment()
TEMPL_ENV.loader = FileSystemLoader(os.path.join(ROOT_DIR, "templates"))

load_template = partial(load_template, env=TEMPL_ENV)


class Render(object):
    """ Collection of renders for templates """

    @staticmethod
    @load_template("qpf")
    @default_args_for_render
    def qpf(meta_info: dict=None,
            revisions: dict=None,
            **kwargs) -> str:
        return kwargs.get('template').render(
            meta_info=meta_info,
            revisions=revisions,
            **kwargs
        )

    @staticmethod
    @load_template("qsf")
    @default_args_for_render
    def qsf(global_assignments: dict=None,
            user_assignments: dict=None,
            **kwargs) -> str:
        return kwargs.get('template').render(
            global_assignments=global_assignments,
            user_assignments=user_assignments,
            **kwargs
        )

    # TODO: legacy?
    @staticmethod
    @load_template("sdc")
    @default_args_for_render
    def sdc(**kwargs) -> NotImplemented:
        """ Throws exception """
        raise NotImplementedError

    @staticmethod
    @load_template("v")
    @default_args_for_render
    def v(project_name: str, **kwargs) -> str:
        return kwargs.get('template').render(
            project_name=project_name,
            **kwargs
        )
