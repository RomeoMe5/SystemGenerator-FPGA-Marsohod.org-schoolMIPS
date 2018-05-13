import os
import subprocess as sp

import click
from flask import Flask

APP_NAME = "web_client"
TRNSL_PATH = os.path.join(APP_NAME, "translation")


def register(app: Flask) -> None:
    """ Register custom cli actions for certain app instance. """

    @app.cli.group()
    def translate() -> None:
        """ Translation and localization commands. """
        pass

    @translate.command()
    @click.argument("lang")
    def init(lang: str) -> None:
        """ Initialize a new language. """
        if sp.call("pybabel extract -F babel.cfg -k _l -o msg.pot ."):
            raise RuntimeError("Extract command failed")

        if sp.call(f"pybabel init -i msg.pot -d {TRNSL_PATH} -l {lang}"):
            raise RuntimeError("Init command failed")

        os.remove("msg.pot")

    @translate.command()
    def update() -> None:
        """ Update all languages. """
        if sp.call("pybabel extract -F babel.cfg -k _l -o msg.pot ."):
            raise RuntimeError("Extract command failed")

        if sp.call(f"pybabel update -i msg.pot -d {TRNSL_PATH}"):
            raise RuntimeError("Update command failed")

        os.remove("msg.pot")

    @translate.command()
    def compile() -> None:
        """ Compile all languages. """
        if sp.call(f"pybabel compile -d {TRNSL_PATH}"):
            raise RuntimeError("Compile command failed")
