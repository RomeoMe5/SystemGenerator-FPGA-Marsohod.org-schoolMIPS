""" Additional methods for preparing engine workflow. """

import asyncio
import io
import json
import os
import shutil
import tarfile
import zipfile
from functools import reduce
from typing import Any, Iterable, NoReturn

import dill
import yaml

from engine.utils.globals import LOGGER, PATHS


class Archiver(object):
    """
        Collection of methods of files' compression.

        Needed to implements specific LOGGER, for more common use
        it's preferable to use shutil.make_archive.
    """

    @staticmethod
    async def _archive(*filenames: Iterable[str],
                       method: str,
                       destination: str,
                       rewrite: bool=True,
                       **kwargs) -> int:
        """ Run checks and apply files' archiving. """
        if not isinstance(destination, str):
            LOGGER.warning("Wrong destination value: '%s'!", type(destination))
            return -2

        if os.path.exists(destination) and not rewrite:
            LOGGER.warning("Destination isn't exists: '%s'!", destination)
            return -1

        if method[0] == "z":
            return await Archiver._to_zip(destination, *filenames, **kwargs)
        elif method[0] == "t":
            return await Archiver._to_tar(destination, *filenames, **kwargs)

        LOGGER.error("Wrong method specified: '%s'!", method)
        raise ValueError(f"Wrong method specified: '{method}'!")

    @staticmethod
    async def _to_zip(path: str,
                      *files: Iterable[str],
                      mode: str=zipfile.ZIP_STORED) -> int:
        successfully_added_count = 0
        with zipfile.ZipFile(path, 'w', compression=mode) as zf_out:
            for filename in files:
                if not isinstance(filename, str):
                    LOGGER.debug("Wrong filename: '%s'!", type(filename))
                elif os.path.isdir(filename):
                    try:
                        for dirname, subdirs, files in os.walk(filename):
                            LOGGER.debug("Add dir '%s' to '%s'.",
                                         dirname, path)
                            zf_out.write(dirname)
                            for file in files:
                                filepath = os.path.join(dirname, file)
                                LOGGER.debug("Add file '%s' to '%s'.",
                                             filepath, path)
                                zf_out.write(filepath)
                                successfully_added_count += 1
                    except BaseException as exc:
                        LOGGER.warning("'%s' wasn't added!\n%s", filename, exc)
                elif os.path.exists(filename):
                    try:
                        LOGGER.debug("Add file '%s' to '%s'.", filename, path)
                        zf_out.write(filename)
                        successfully_added_count += 1
                    except tarfile.TarError as exc:
                        LOGGER.warning("'%s' wasn't added!\n%s", filename, exc)
                else:
                    LOGGER.warning("File isn't exists: '%s'.", filename)
        return successfully_added_count

    @staticmethod
    async def _to_tar(path: str, *files: Iterable[str], mode: str="w") -> int:
        successfully_added_count = 0
        with tarfile.open(path, mode) as tar_fout:
            for filename in files:
                if not isinstance(filename, str):
                    LOGGER.warning("Wrong filename: '%s'!", type(filename))
                elif os.path.exists(filename):
                    try:
                        LOGGER.debug("Add file '%s' to '%s'.", filename, path)
                        tar_fout.add(filename)
                        successfully_added_count += 1
                    except tarfile.TarError as exc:
                        LOGGER.debug("'%s' wasn't added!\n%s", filename, exc)
                else:
                    LOGGER.warning("File isn't exists: '%s'.", filename)
        return successfully_added_count

    @staticmethod
    async def get_tar_io(files: dict) -> io.BytesIO:
        """ Returns tar file I/O """
        LOGGER.debug("Create tar I/O")
        tar_io = io.BytesIO()
        with tarfile.open(fileobj=tar_io, mode="w") as tar_fout:
            for filename, file_line in files.items():
                try:
                    if isinstance(file_line, dict):
                        for fname, fline in file_line.items():
                            LOGGER.debug("Add '%s' to tar I/O", fname)
                            tar_fout.addfile(
                                tarfile.TarInfo(os.path.join(filename, fname)),
                                fileobj=io.BytesIO(fline.encode("utf-8"))
                            )
                    else:
                        LOGGER.debug("Add file '%s' to tar I/O", filename)
                        tarinfo = tarfile.TarInfo(filename)
                        tarinfo.size = io.StringIO().write(file_line)
                        tar_fout.addfile(
                            tarinfo,
                            fileobj=io.BytesIO(file_line.encode("utf-8"))
                        )
                except tarfile.TarError as exc:
                    LOGGER.warning("'%s' wasn't added!\n%s", filename, exc)
        return tar_io

    @staticmethod
    async def to_tar_flow(files: dict, path: str, mips: dict=None) -> NoReturn:
        """ Write tar I/O to tar file """
        with open(path + ".tar", 'wb') as tar_fout:
            LOGGER.debug("Creating '%s' tar file", path)
            tar_fout.write((await Archiver.get_tar_io(files)).getvalue())
            LOGGER.info("'%s' file created", path)

    @staticmethod
    async def archive(destination: str,
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

        if method not in {"tar", "zip"}:
            LOGGER.debug(
                "'%s' archiving detected [without compression].",
                method
            )
            method, compression = compression, None

        params = {
            'method': method[0],
            'destination': destination,
            'rewrite': rewrite
        }

        if compression:
            LOGGER.debug(
                "'%s' archiving detected [with %s compression].",
                method,
                compression
            )
            compression = compression[0]
            if method == "z":
                if compression == "d":
                    params['mode'] = zipfile.ZIP_DEFLATED
                elif compression == "b":
                    params['mode'] = zipfile.ZIP_BZIP2
                elif compression == "l":
                    params['mode'] = zipfile.ZIP_LZMA
            elif method == "t":
                if compression == "b":
                    params['mode'] = "w:bz2"
                elif compression == "x":
                    params['mode'] = "w:xz"
                elif compression == "g":
                    params['mode'] = "w:gz"

        return await Archiver._archive(*filenames, **params)

    # [minor] TODO implement extraction
    # NOTE this function signature refer to public method
    #      but was hidden until method will be finished
    @staticmethod
    async def _extract(path: str, destination: str=".", **kwargs) -> int:
        """
            Extracs files from archive.

            :return number of extracted files.
        """
        method, compression = path.lower().split('.')[-2:]
        raise NotImplementedError


class Convertor(object):
    """ Collection of methods to convert static files formats. """
    LOADERS = {
        'json': json.load,
        'yml': yaml.load,
        'bin': dill.load
    }
    DUMPERS = {
        'json': json.dump,
        'yml': yaml.dump,
        'bin': dill.dump
    }

    @staticmethod
    async def _load_content(path: str, fmt: str=None) -> object:
        """ Try to guess file format and load file content. """
        if fmt is None or fmt not in Convertor.LOADERS:
            fmt = path.split('.')[-1]
            if fmt in Convertor.LOADERS:
                LOGGER.debug("Detect file format: %s", fmt)
            else:
                LOGGER.debug("Can't detect file format from '%s'", path)
                fmt = None

        if fmt is None:
            for extension, loader in Convertor.LOADERS.items():
                _path = path
                if not _path.endswith(extension):
                    LOGGER.debug("Assume file has '%s' extension", extension)
                    _path = ".".join((_path, extension))

                try:
                    with open(_path, 'rb') as fin:
                        return loader(fin)
                except BaseException as exc:
                    LOGGER.error(exc)
            raise IOError(f"Can't load file content: '{path}'!")

        with open(path, 'rb') as fin:
            return Convertor.LOADERS[fmt](fin)

    @staticmethod
    async def convert(from_path: str,
                      to_fmt: str,
                      to_path: str=None,
                      from_fmt: str=None) -> NoReturn:
        """ Convert static files formats. """
        content = await Convertor._load_content(from_path, from_fmt)

        if to_path is None:
            to_path = ".".join(from_path.split('.')[:-1])
            LOGGER.debug("Assume destination path is: '%s'", to_path)

        if not to_path.endswith(to_fmt):
            to_path = ".".join((to_path, to_fmt))

        mode = 'w' if to_fmt != 'bin' else 'wb'
        with open(to_path, mode) as fout:
            LOGGER.debug("Save converted file to: '%s'", to_path)
            Convertor.DUMPERS[to_fmt](content, fout)
            LOGGER.info("Converted file saved to: '%s'", to_path)


class Loader(object):
    """ Implements file content loading """

    # [minor] TODO add "xml", "csv"
    # NOTE ordered by significance (priority)
    FORMATS = ("yml", "json", "bin")
    LOADERS = {
        'yml': yaml.load,
        'json': json.load,
        'bin': dill.load
    }

    @staticmethod
    async def load(filepath: str,
                   loader_params: dict=None,
                   **kwargs) -> Any:
        """ Loads content of static file from any location """
        file_format = filepath.split('.')[-1].lower()
        loader_params = loader_params or {}
        with open(filepath, 'rb', **kwargs) as fin:
            LOGGER.debug("Loading '%s' content...", filepath)
            for extension in Loader.FORMATS:
                if file_format == extension:
                    return Loader.LOADERS[extension](fin, **loader_params)
            return fin.read()  # read plain text

    @staticmethod
    async def load_static(path: str,
                          path_to_static: str=None,
                          loader_params: dict=None,
                          encoding: str=None,
                          **kwargs) -> Any:
        """ Loads content of static file from engine 'static' folder """
        filepath = path
        if path_to_static is not None:
            filepath = await Loader.get_static_path(path, path_to_static)
        content = await Loader.load(filepath, loader_params, **kwargs)
        return content.decode(encoding) if encoding is not None else content

    @staticmethod
    async def get_static_path(filename: str,
                              path_to_static: str=PATHS.STATIC) -> str:
        """ Return path for static object (if it exists) """
        path = os.path.join(path_to_static, filename)

        if os.path.exists(path):
            return path

        for extension in Loader.FORMATS:
            if not filename.endswith(extension):
                LOGGER.debug("Assume file has '%s' extension.", extension)
                path = ".".join((path, extension))
                if os.path.exists(path):
                    return path

        LOGGER.error("'%s' isn't exists!", path)
        raise FileNotFoundError(f"'{path}' isn't exists!")


def create_dirs(*paths: Iterable[str], rewrite: bool=False) -> int:
    """ :return number of errors """
    async def create_dir(path: str) -> bool:
        """ :return error occures """
        if not isinstance(path, str):
            LOGGER.error("Wrong path specified: '%s'", path)
            return True
        elif os.path.exists(path) and rewrite:
            try:
                LOGGER.debug("Remove '%s'.", path)
                shutil.rmtree(path)
            except BaseException as exc:
                LOGGER.warning("Can't remove '%s'!\n%s", path, exc)
                return True
        elif os.path.exists(path):
            LOGGER.debug("Skip '%s' as it's exists.", path)
            return True

        try:
            LOGGER.debug("Create '%s' folder.", path)
            os.mkdir(path)
            LOGGER.info("Folder created: '%s'.", path)
        except BaseException as exc:
            LOGGER.warning("Can't create '%s'!\n%s", path, exc)
            return True
        return False

    tasks = (create_dir(path) for path in paths)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(asyncio.gather(*tasks))
    return reduce(lambda x, y: x + int(y), res)
