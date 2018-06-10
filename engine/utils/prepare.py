""" Additional methods for preparing engine workflow. """

import io
import json
import os
import shutil
import tarfile
import zipfile

import dill
import yaml

try:
    from engine.utils.log import LOGGER
except ImportError as err:
    import logging as LOGGER


class Archiver(object):
    """
        Collection of methods of files' compression.

        Needed to implements specific LOGGER, for more common use
        it's preferable to use shutil.make_archive.
    """

    @staticmethod
    def _archive(*filenames,
                 method: str,
                 destination: str,
                 rewrite: bool=True,
                 **kwargs) -> int:
        """ Run checks and apply files' archiving. """
        if not isinstance(destination, str):
            LOGGER.error("Wrong destination value: '%s'!", type(destination))
            return -2

        if os.path.exists(destination) and not rewrite:
            LOGGER.warning("Destination isn't exists: '%s'!", destination)
            return -1

        if method[0] == "z":
            return Archiver._to_zip(destination, *filenames, **kwargs)
        elif method[0] == "t":
            return Archiver._to_tar(destination, *filenames, **kwargs)

        LOGGER.error("Wrong method specified: '%s'!", method)
        raise ValueError("Wrong method specified: '{}'!".format(method))

    @staticmethod
    def _to_zip(path: str, *files, mode: str=zipfile.ZIP_STORED) -> int:
        successfully_added_count = 0
        with zipfile.ZipFile(path, 'w', compression=mode) as zf_out:
            for filename in files:
                if not isinstance(filename, str):
                    LOGGER.error("Wrong filename: '%s'!", type(filename))
                elif os.path.isdir(filename):
                    try:
                        for dirname, subdirs, files in os.walk(filename):
                            zf_out.write(dirname)
                            LOGGER.debug(
                                "Add dir '%s' to '%s'.",
                                dirname,
                                path
                            )
                            for file in files:
                                filepath = os.path.join(dirname, file)
                                zf_out.write(filepath)
                                successfully_added_count += 1
                                LOGGER.debug(
                                    "Add file '%s' to '%s'.",
                                    filepath,
                                    path
                                )
                    except BaseException as err:
                        LOGGER.error("'%s' wasn't added!\n%s", filename, err)
                elif os.path.exists(filename):
                    try:
                        zf_out.write(filename)
                        successfully_added_count += 1
                        LOGGER.debug("Add file '%s' to '%s'.", filename, path)
                    except tarfile.TarError as err:
                        LOGGER.error("'%s' wasn't added!\n%s", filename, err)
                else:
                    LOGGER.warning("File isn't exists: '%s'.", filename)
        return successfully_added_count

    @staticmethod
    def get_tar_io(files: dict) -> io.BytesIO:
        """ Returns tar file I/O """
        tar_io = io.BytesIO()
        LOGGER.info("Create tar I/O")
        with tarfile.open(fileobj=tar_io, mode="w") as tar_fout:
            for file_name, file_line in files.items():
                try:
                    tarinfo = tarfile.TarInfo(file_name)
                    file_line_byte = io.BytesIO(file_line.encode('utf-8'))
                    tarinfo.size = io.StringIO().write(file_line)
                    tar_fout.addfile(tarinfo, fileobj=file_line_byte)
                    LOGGER.debug(
                        "   Add file '%s' to tar I/O, content(binary): '%s",
                        file_name, file_line_byte)
                except tarfile.TarError as err:
                    LOGGER.error("'%s' wasn't added!\n%s", file_name, err)
        LOGGER.debug("Return tar I/O")
        return tar_io

    @staticmethod
    def to_tar_flow(files: dict,
                    path: str,
                    in_memory=False) -> io.BytesIO:
        """ Write tar I/O to tar file """
        tar_io = Archiver.get_tar_io(files)
        if not in_memory:
            with open(path + ".tar", 'wb') as tar_fout:
                LOGGER.info("Create '%s'.tar file", path)
                tar_fout.write(tar_io.getvalue())
                LOGGER.debug("Adding tar I/O to '%s'.tar file", path)
        return tar_io

    @staticmethod
    def _to_tar(path: str, *files, mode: str="w") -> int:
        successfully_added_count = 0
        with tarfile.open(path, mode) as tar_fout:
            for filename in files:
                if not isinstance(filename, str):
                    LOGGER.error("Wrong filename: '%s'!", type(filename))
                elif os.path.exists(filename):
                    try:
                        tar_fout.add(filename)
                        successfully_added_count += 1
                        LOGGER.debug(
                            "Add file '%s' to '%s'.", filename, path)
                    except tarfile.TarError as err:
                        LOGGER.error(
                            "'%s' wasn't added!\n%s", filename, err)
                else:
                    LOGGER.warning("File isn't exists: '%s'.", filename)
        return successfully_added_count

    @staticmethod
    def archive(destination: str, *filenames, rewrite: bool=True) -> int:
        """
            Archive files to destination path.

            Automatically detect archiving and compression methods
            from destination file name.

            Supported compressions: bzip2, gzip, lzma,
            zip (zip archive only), tar (tar archive only)
        """
        method, compression = destination.lower().split('.')[-2:]

        if method not in {"tar", "zip"}:
            method, compression = compression, None
            LOGGER.debug(
                "'%s' archiving detected [without compression].",
                method
            )

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

        return Archiver._archive(*filenames, **params)

    # [minor] TODO: implement extraction
    @staticmethod
    def _extract(path: str, destination: str=".", **kwargs) -> int:
        # Note: this function signature refer to public method
        # but was hidden until method will be finished
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
    def _load_content(path: str, fmt: str=None) -> object:
        """ Try to guess file format and load file content. """
        if fmt is None or fmt not in Convertor.LOADERS:
            fmt = path.split('.')[-1]
            if fmt in Convertor.LOADERS:
                LOGGER.debug("Detect file format: %s", fmt)
            else:
                fmt = None
                LOGGER.debug("Can't detect file format from '%s'", path)

        if fmt is None:
            for extension, loader in Convertor.LOADERS.items():
                _path = path
                if not _path.endswith(extension):
                    _path = ".".join((_path, extension))
                    LOGGER.debug("Assume file has '%s' extension", extension)

                try:
                    with open(_path, 'rb') as fin:
                        return loader(fin)
                except BaseException as err:
                    LOGGER.warning(err)
            raise IOError(f"Can't load file content: '{path}'!")

        with open(path, 'rb') as fin:
            return Convertor.LOADERS[fmt](fin)

    @staticmethod
    def convert(from_path: str,
                to_fmt: str,
                to_path: str=None,
                from_fmt: str=None) -> None:
        """ Convert static files formats. """
        content = Convertor._load_content(from_path, from_fmt)

        if to_path is None:
            to_path = ".".join(from_path.split('.')[:-1])
            LOGGER.debug("Assume destination path is: '%s'", to_path)

        if not to_path.endswith(to_fmt):
            to_path = ".".join((to_path, to_fmt))

        mode = 'w' if to_fmt != 'bin' else 'wb'
        with open(to_path, mode) as fout:
            Convertor.DUMPERS[to_fmt](content, fout)
            LOGGER.info("Converted file saved to: '%s'", to_path)


def create_dirs(*paths, rewrite: bool=False) -> int:
    """ Create folders. """
    successfully_created_count = 0
    for path in paths:
        if not isinstance(path, str):
            LOGGER.error("Wrong path specified: '%s'", type(path))
            continue
        elif os.path.exists(path) and rewrite:
            try:
                shutil.rmtree(path)
                LOGGER.debug("Remove '%s'.", path)
            except BaseException as err:
                LOGGER.error("Can't remove '%s'!\n%s", path, err)
                continue
        elif os.path.exists(path):
            LOGGER.info("Skip '%s' as it's exists.", path)
            continue

        try:
            os.mkdir(path)
            successfully_created_count += 1
            LOGGER.debug("Create '%s' folder.", path)
        except BaseException as err:
            LOGGER.error("Can't create '%s'!\n%s", path, err)

        return successfully_created_count
