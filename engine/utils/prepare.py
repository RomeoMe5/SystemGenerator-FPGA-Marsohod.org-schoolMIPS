""" Additional methods for preparing engine workflow. """

import io
import logging
import os
import shutil
import tarfile
import zipfile
from functools import reduce
from typing import Any, Iterable, NoReturn

import yaml

from engine.constants import PATHS, PROJECT_NAME_PATTERN


class Archiver(object):
    """
        Collection of methods of files' compression.

        Needed to implements specific logging, for more common use
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
            logging.warning("Wrong destination value: '%s'", type(destination))
            return -1

        if os.path.exists(destination) and not rewrite:
            logging.warning("Destination isn't exists: '%s'", destination)
            return -2

        if method[0] == "t":
            return Archiver._to_tar(destination, *filenames, **kwargs)
        if method[0] == "z":
            return Archiver._to_zip(destination, *filenames, **kwargs)

        logging.warning("Wrong method specified: '%s'", method)
        return -3

    @staticmethod
    def _to_zip(path: str,
                *files: Iterable[str],
                mode: int=zipfile.ZIP_STORED) -> int:
        def add_to_archive(filename: str, archive: object) -> bool:
            logging.debug("Add file '%s' to '%s'", filename, path)
            try:
                archive.write(filename)
            except tarfile.TarError as exc:
                logging.warning("'%s' wasn't added\n%s", filename, exc)
                return True
            return False

        errors_count = 0
        with zipfile.ZipFile(path, "w", compression=mode) as zf_out:
            for filename in files:
                if not os.path.exists(filename):
                    logging.debug("File isn't exists: '%s'", filename)
                    errors_count += 1
                    continue
                if not os.path.isdir(filename):
                    errors_count += add_to_archive(filename, zf_out)
                    continue
                for dirname, subdirs, files in os.walk(filename):
                    logging.debug("Add dir '%s' to '%s'", dirname, path)
                    try:
                        zf_out.write(dirname)
                        errors_count += reduce(
                            lambda x, y: x + y,
                            map(lambda x: add_to_archive(
                                os.path.join(dirname, x), zf_out
                            ), files)
                        )
                    # [minor] TODO use specific exception
                    except BaseException as e:
                        logging.warning("'%s' wasn't added:\n%s", filename, e)
                        errors_count += 1
        return errors_count

    @staticmethod
    def _to_tar(path: str, *files: Iterable[str], mode: str="w") -> int:
        def add_to_archive(filename: str, archive: object) -> bool:
            if not os.path.exists(filename):
                logging.warning("File isn't exists: '%s'", filename)
                return True
            logging.debug("Add file '%s' to '%s'", filename, path)
            try:
                archive.add(filename)
            except tarfile.TarError as e:
                logging.debug("'%s' wasn't added:\n%s", filename, e)
                return True
            return False

        added_count = 0
        with tarfile.open(path, mode) as tar_fout:
            return reduce(lambda x, y: x + y,
                          map(lambda x: add_to_archive(x, tar_fout), files))

    @staticmethod
    def get_tar_io(files: dict) -> io.BytesIO:
        """ Returns tar file I/O """
        logging.debug("Create tar I/O")
        with tarfile.open(fileobj=io.BytesIO(), mode="w") as tar_fout:
            for filename, file_line in files.items():
                try:
                    if isinstance(file_line, dict):
                        for fname, fline in file_line.items():
                            logging.debug("Add '%s' to tar I/O", fname)
                            tar_fout.addfile(
                                tarfile.TarInfo(os.path.join(filename, fname)),
                                fileobj=io.BytesIO(fline.encode("utf-8"))
                            )
                        continue
                    logging.debug("Add file '%s' to tar I/O", filename)
                    tarinfo = tarfile.TarInfo(filename)
                    tarinfo.size = io.StringIO().write(file_line)
                    tar_fout.addfile(
                        tarinfo,
                        fileobj=io.BytesIO(file_line.encode("utf-8"))
                    )
                except tarfile.TarError as e:
                    logging.warning("'%s' wasn't added:\n%s", filename, e)
            return tar_fout.fileobj

    @staticmethod
    def to_tar_flow(files: dict, path: str) -> NoReturn:
        """ Write tar I/O to tar file """
        if not path.endswith(".tar"):
            path += ".tar"
        logging.debug("Creating '%s' tar file", path)
        with open(path, "wb") as tar_fout:
            tar_fout.write(Archiver.get_tar_io(files).getvalue())
            logging.info("'%s' file created", path)

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
            logging.debug("'%s' archiving detected [without compression]",
                          method)
            method, compression = compression, None

        params = {
            'method': method[0],
            'destination': destination,
            'rewrite': rewrite
        }

        if compression:
            logging.debug("'%s' archiving detected [with %s compression]",
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

    @staticmethod
    def _is_file(path: str) -> bool:
        if not os.path.exists(path):
            raise FileNotFoundError("File '%s' isn't exist", path)
        if not os.path.isfile(path):
            raise ValueError("Is not a file '%s'", path)

    @staticmethod
    def load(path: str, encoding: str="utf-8", **kwargs) -> Any:
        """ Loads content of static file (yaml or plain text if encoding) """
        logging.debug("Loading content from '%s'", path)
        Loader._is_file(path)
        with open(path, "rb", **kwargs) as fin:
            if encoding:
                logging.debug("Load '%s' as plain text with '%s' encoding",
                              path, encoding)
                return fin.read().decode(encoding)
            logging.debug("Load '%s' as yaml", path)
            return yaml.load(fin)

    @staticmethod
    def get_static_path(filename: str,
                        path_to_static: str=PATHS.STATIC) -> str or NoReturn:
        """ Return path for static object (if it exists) """
        path = os.path.join(path_to_static, filename)
        logging.debug("Static path is '%s'", path)
        Loader._is_file(path)
        return path


def create_dirs(*paths: Iterable[str], rewrite: bool=False) -> int:
    """ :return number of errors """

    def create_dir(path: str) -> int:
        """ :return error occures """
        if os.path.exists(path) and rewrite:
            logging.debug("Remove folder '%s'", path)
            try:
                shutil.rmtree(path)
            except BaseException as e:
                logging.error("Can't remove folder '%s': %s", path, e)
                return 1
        elif os.path.exists(path):
            logging.debug("Skip folder '%s' as it already exists", path)
            return 1

        logging.debug("Create '%s' folder", path)
        try:
            os.mkdir(path)
        except BaseException as e:
            logging.error("Can't create folder '%s': %s", path, e)
            return 1
        logging.info("Folder '%s' created", path)
        return 0

    return reduce(lambda x, y: x + y, map(create_dir, paths))


def validate_project_name(name: str) -> bool:
    return PROJECT_NAME_PATTERN.match(name)
