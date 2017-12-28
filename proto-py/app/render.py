import os
from functools import partial
from jinja2 import Environment, FileSystemLoader

from app import ROOT_DIR
from app.utils.decorators import default_args_for_render, load_template

TEMPL_DIR = os.path.join(ROOT_DIR, "templates")
TEMPL_ENV = Environment()
TEMPL_ENV.loader = FileSystemLoader(TEMPL_DIR)

load_template = partial(load_template, env=TEMPL_ENV)


@load_template("qpf")
@default_args_for_render
def render_qpf(meta_info: dict=None,
               revisions: dict=None,
               **kwargs) -> str:
    return kwargs.get('template').render(
        meta_info=meta_info,
        revisions=revisions,
        **kwargs
    )


@load_template("qsf")
@default_args_for_render
def render_qsf(global_assignments: dict=None,
               user_assignments: dict=None,
               **kwargs) -> str:
    return kwargs.get('template').render(
        global_assignments=global_assignments,
        user_assignments=user_assignments,
        **kwargs
    )


# TODO: legacy?
@load_template("sdc")
@default_args_for_render
def render_sdc(**kwargs) -> NotImplemented:
    """ Throws exception """
    raise NotImplementedError


@load_template("v")
@default_args_for_render
def render_v(project_name: str, **kwargs) -> str:
    return kwargs.get('template').render(project_name=project_name, **kwargs)
