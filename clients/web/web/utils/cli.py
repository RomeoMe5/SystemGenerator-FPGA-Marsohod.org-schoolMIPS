import os
import subprocess
from pprint import pprint
from typing import NoReturn

import click
from flask import Flask

from web_client import APP_NAME, PATHS
from web_client.models import MODELS
from web_client.utils.serialize import Serializer


TEMP_FILE = os.path.join(PATHS.TRANSL, "msg.pot")


def register(app: Flask, config: str="babel.cfg") -> NoReturn:
    """ Register custom cli actions for certain app instance. """

    @app.cli.group()
    def translate() -> NoReturn:
        """ Translation and localization commands. """

    @translate.command()
    @click.argument("lang")
    def init(lang: str) -> NoReturn:
        f""" Initialize a new language. {config} should exists!. """
        cmd = f"pybabel extract -F {config} -k _l -o {TEMP_FILE} ."
        if subprocess.call(cmd):
            raise RuntimeError("Extract command failed")

        app.logger.debug("Initiate new translation for %s language", lang)
        cmd = f"pybabel init -i {TEMP_FILE} -d {PATHS.TRANSL} -l {lang}"
        if subprocess.call(cmd):
            raise RuntimeError("Init command failed")

        os.remove(TEMP_FILE)

    @translate.command()
    def update() -> NoReturn:
        f""" Update all languages. {config} should exists! """
        app.logger.debug("Update strings for translation")
        cmd = f"pybabel extract -F {config} -k _l -o {TEMP_FILE} ."
        if subprocess.call(cmd):
            raise RuntimeError("Extract command failed")

        cmd = f"pybabel update -i {TEMP_FILE} -d {PATHS.TRANSL}"
        if subprocess.call(cmd):
            raise RuntimeError("Update command failed")

        os.remove(TEMP_FILE)

    @translate.command()
    def compile() -> NoReturn:
        """ Compile all languages. """
        app.logger.debug("Compile all translations")
        cmd = f"pybabel compile -d {PATHS.TRANSL}"
        if subprocess.call(cmd):
            raise RuntimeError("Compile command failed")

    @app.cli.group()
    def dump() -> NoReturn:
        """ Database data dump manipulations. """

    @dump.command()
    @click.argument("path")
    def create(path: str) -> NoReturn:
        """ Create new dump of app database. """
        app.logger.debug("Create new database dump to: %s", path)
        Serializer.dump(path, *MODELS)

    @dump.command()
    @click.argument("path")
    def load(path: str) -> NoReturn:
        """ Load database state from dump. """
        app.logger.debug("Load database state from: %s", path)
        Serializer.load(path, *MODELS)

    @dump.command()
    @click.argument("path")
    def show(path: str) -> NoReturn:
        """ Show database dump content. """
        app.logger.debug("Load database from: %s", path)
        payload = Serializer.show(path)
        pprint({model.__name__: data for model, data in zip(MODELS, payload)})
