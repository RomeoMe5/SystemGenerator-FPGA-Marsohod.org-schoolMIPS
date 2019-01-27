""" Additional methods for preparing engine workflow. """

import io
import json
import os
import shutil
import tarfile
import zipfile
from collections import OrderedDict
from functools import reduce
from typing import Any, Iterable, NoReturn

import dill
import yaml

from fpga_marsohod_generator_engine.constants import PATHS
from fpga_marsohod_generator_engine.utils.misc import LOGGER


class Archiver(object):
    """
        Collection of methods of files' compression.

        Needed to implements specific LOGGER, for more common use
        it's preferable to use shutil.make_archive.
    """

    @staticmethod
    def _archive(*filenames: Iterable[str],
                 method: str,
                 destination: str,
                 rewrite: bool=True,
                 **kwargs) -> int:
        """ Run checks and apply files' archiving. """
        if not isinstance(destination, str):
            LOGGER.warning("Wrong destination value: '%s'!", type(destination))
            return -1

        if os.path.exists(destination) and not rewrite:
            LOGGER.warning("Destination isn't exists: '%s'!", destination)
            return -2

        if method[0] == "t":
            return Archiver._to_tar(destination, *filenames, **kwargs)
        if method[0] == "z":
            return Archiver._to_zip(destination, *filenames, **kwargs)

        LOGGER.warning("Wrong method specified: '%s'!", method)
        return -3

    @staticmethod
    def _to_zip(path: str,
                *files: Iterable[str],
                mode: int=zipfile.ZIP_STORED) -> int:
        def add_to_archive(filename: str, archive: object) -> bool:
            LOGGER.debug("Add file '%s' to '%s'.", filename, path)
            try:
                archive.write(filename)
            except tarfile.TarError as exc:
                LOGGER.warning("'%s' wasn't added!\n%s", filename, exc)
                return True
            return False

        errors_count = 0
        with zipfile.ZipFile(path, "w", compression=mode) as zf_out:
            for filename in files:
                if not os.path.exists(filename):
                    LOGGER.debug("File isn't exists: '%s'.", filename)
                    errors_count += 1
                    continue
                if not os.path.isdir(filename):
                    errors_count += add_to_archive(filename, zf_out)
                    continue
                for dirname, subdirs, files in os.walk(filename):
                    LOGGER.debug("Add dir '%s' to '%s'.", dirname, path)
                    try:
                        zf_out.write(dirname)
                        errors_count += reduce(
                            lambda x, y: x + y,
                            map(lambda x: add_to_archive(
                                os.path.join(dirname, x), zf_out
                            ), files)
                        )
                    # [minor] TODO use specific exception
                    except BaseException as exc:
                        LOGGER.warning("'%s' wasn't added!\n%s", filename, exc)
                        errors_count += 1
        return errors_count

    @staticmethod
    def _to_tar(path: str, *files: Iterable[str], mode: str="w") -> int:
        def add_to_archive(filename: str, archive: object) -> bool:
            if not os.path.exists(filename):
                LOGGER.warning("File isn't exists: '%s'.", filename)
                return True
            LOGGER.debug("Add file '%s' to '%s'.", filename, path)
            try:
                archive.add(filename)
            except tarfile.TarError as exc:
                LOGGER.debug("'%s' wasn't added!\n%s", filename, exc)
                return True
            return False

        added_count = 0
        with tarfile.open(path, mode) as tar_fout:
            return reduce(lambda x, y: x + y,
                          map(lambda x: add_to_archive(x, tar_fout), files))

    @staticmethod
    def get_tar_io(files: dict) -> io.BytesIO:
        """ Returns tar file I/O """
        LOGGER.debug("Create tar I/O")
        with tarfile.open(fileobj=io.BytesIO(), mode="w") as tar_fout:
            for filename, file_line in files.items():
                try:
                    if isinstance(file_line, dict):
                        for fname, fline in file_line.items():
                            LOGGER.debug("Add '%s' to tar I/O", fname)
                            tar_fout.addfile(
                                tarfile.TarInfo(os.path.join(filename, fname)),
                                fileobj=io.BytesIO(fline.encode("utf-8"))
                            )
                        continue
                    LOGGER.debug("Add file '%s' to tar I/O", filename)
                    tarinfo = tarfile.TarInfo(filename)
                    tarinfo.size = io.StringIO().write(file_line)
                    tar_fout.addfile(
                        tarinfo,
                        fileobj=io.BytesIO(file_line.encode("utf-8"))
                    )
                except tarfile.TarError as exc:
                    LOGGER.warning("'%s' wasn't added!\n%s", filename, exc)
            return tar_fout.fileobj

    @staticmethod
    def to_tar_flow(files: dict, path: str) -> NoReturn:
        """ Write tar I/O to tar file """
        if not path.endswith(".tar"):
            path += ".tar"
        LOGGER.debug("Creating '%s' tar file", path)
        with open(path, "wb") as tar_fout:
            tar_fout.write((Archiver.get_tar_io(files)).getvalue())
            LOGGER.info("'%s' file created", path)

    @staticmethod
    def archive(destination: str,
                *filenames: Iterable[str],
                rewrite: bool=True) -> int:
        """
            Archive files to destination path.

            Automatically detect archiving and compression methods
            from destination file name.

            Supported compressions: bzip2, gzip, lzma,
            zip (zip archive only), tar (tar archive only)
        """
        method, compression = destination.lower().split('.')[-2:]

        if method[0] not in "zt":
            LOGGER.debug("'%s' archiving detected [without compression].",
                         method)
            method, compression = compression, None

        params = {
            'method': method[0],
            'destination': destination,
            'rewrite': rewrite
        }

        if compression:
            LOGGER.debug("'%s' archiving detected [with %s compression].",
                         method,
                         compression)
            compression = compression[0]
            if "z" in method:
                if "d" in compression:
                    params['mode'] = zipfile.ZIP_DEFLATED
                elif "b" in compression:
                    params['mode'] = zipfile.ZIP_BZIP2
                elif "l" in compression:
                    params['mode'] = zipfile.ZIP_LZMA
            elif "t" in method:
                if "b" in compression:
                    params['mode'] = "w:bz2"
                elif "x" in compression:
                    params['mode'] = "w:xz"
                elif "g" in compression:
                    params['mode'] = "w:gz"

        return Archiver._archive(*filenames, **params)

    # [minor] TODO implement extraction
    # NOTE this function signature refer to public method
    #      but was hidden until method will be finished
    @staticmethod
    def _extract(path: str, destination: str=".", **kwargs) -> int:
        """
            Extracs files from archive.

            :return number of extracted files.
        """
        method, compression = path.lower().split('.')[-2:]
        raise NotImplementedError


class Loader(object):
    """ Implements file content loading """

    LOADERS = OrderedDict(
        yml=yaml.load,
        json=json.load,
        bin=dill.load
    )
    DUMPERS = OrderedDict(
        yml=yaml.dump,
        json=json.dump,
        bin=dill.dump
    )

    @staticmethod
    def load(filepath: str,
             fmt: str=None,
             loader_params: dict=None,
             **kwargs) -> Any:
        """ Loads content of static file from any location """
        if fmt is None or fmt not in Loader.LOADERS:
            LOGGER.debug("Try to detect file format from file: %s", filepath)
            fmt = filepath.split('.')[-1].lower()
            if fmt in Loader.LOADERS:
                LOGGER.debug("Detect file format: %s", fmt)
            else:
                LOGGER.debug("Can't detect file format from '%s'", filepath)
                fmt = None
                LOGGER.debug("Try to detect file format from loaders")
                for _fmt in Loader.LOADERS:
                    _path = filepath + "." + _fmt
                    if os.path.exists(_path):
                        LOGGER.debug("Assume file has '%s' fmt", _fmt)
                        filepath = _path
                        fmt = _fmt
                        break

        LOGGER.debug("Loading '%s' content...", filepath)
        with open(filepath, "rb", **kwargs) as fin:
            if fmt is None:
                LOGGER.debug("Read %s as plain text", filepath)
                return fin.read()  # read plain text
            return Loader.LOADERS[fmt](fin, **(loader_params or {}))

    @staticmethod
    def load_static(path: str,
                    path_to_static: str=None,
                    loader_params: dict=None,
                    encoding: str="utf-8",
                    **kwargs) -> Any:
        """ Loads content of static file from engine 'static' folder """
        if path_to_static is not None:
            path = Loader.get_static_path(path, path_to_static)
        content = Loader.load(path, loader_params, **kwargs)
        return content.decode(encoding) if encoding is not None else content

    @staticmethod
    def get_static_path(filename: str,
                        path_to_static: str=PATHS.STATIC) -> str or NoReturn:
        """ Return path for static object (if it exists) """
        path = os.path.join(path_to_static, filename)
        if os.path.exists(path):
            return path

        for fmt in Loader.LOADERS:
            LOGGER.debug("Assume file '%s' has '%s' extension.", path, fmt)
            _path = path + "." + fmt
            if os.path.exists(_path):
                return _path

        LOGGER.error("'%s' isn't exists!", path)


def convert(from_path: str,
            to_fmt: str,
            to_path: str=None,
            from_fmt: str=None) -> NoReturn:
    """ Convert static files formats. """
    if not os.path.exists(from_path):
        LOGGER.error("Target file %s isn't exist", from_path)
        return

    content = Loader.load(from_path, fmt=from_fmt)

    if to_path is None:
        to_path = ".".join(from_path.split('.')[:-1])
        LOGGER.debug("Assume destination path is: '%s'", to_path)

    if not to_path.endswith(to_fmt):
        to_path = to_path + "." + to_fmt

    LOGGER.debug("Save converted file to: '%s'", to_path)
    with open(to_path, ("w" if to_fmt != "bin" else "wb")) as fout:
        Loader.DUMPERS[to_fmt](content, fout)
        LOGGER.info("Converted file saved to: '%s'", to_path)


def create_dirs(*paths: Iterable[str], rewrite: bool=False) -> int:
    """ :return number of errors """

    def create_dir(path: str) -> bool:
        """ :return error occures """
        if not isinstance(path, str):
            LOGGER.error("Wrong path specified: '%s'", path)
            return True
        elif os.path.exists(path) and rewrite:
            LOGGER.debug("Remove '%s'.", path)
            try:
                shutil.rmtree(path)
            except BaseException as exc:
                LOGGER.warning("Can't remove '%s'!\n%s", path, exc)
                return True
        elif os.path.exists(path):
            LOGGER.debug("Skip '%s' as it's exists.", path)
            return True

        LOGGER.debug("Create '%s' folder.", path)
        try:
            os.mkdir(path)
        except BaseException as exc:
            LOGGER.warning("Can't create '%s'!\n%s", path, exc)
            return True
        LOGGER.info("Folder created: '%s'.", path)
        return False

    return reduce(lambda x, y: x + y, map(create_dir, paths))
