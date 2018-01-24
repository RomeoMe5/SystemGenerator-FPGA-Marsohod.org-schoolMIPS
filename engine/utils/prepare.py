import logging
import os
import tarfile
import zipfile


class Compressor(object):
    """
        Collection of methods of files' compression.

        Needed to implements specific logging, for more common use
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
            logging.error("Wrong destination value: '%s'!", type(destination))
            return -2

        if os.path.exists(destination) and not rewrite:
            logging.warning("Destination isn't exists: '%s'!", destination)
            return -1

        if method[0] == "z":
            return Compressor._to_zip(destination, *filenames, **kwargs)
        elif method[0] == "t":
            return Compressor._to_tar(destination, *filenames, **kwargs)

        logging.error("Wrong method specified: '%s'!", method)
        raise ValueError("Wrong method specified: '{}'!".format(method))

    @staticmethod
    def _to_zip(path: str, *files, mode: str=zipfile.ZIP_STORED) -> int:
        count_files = 0
        with zipfile.ZipFile(path, 'w', compression=mode) as zf_out:
            for filename in files:
                if not isinstance(filename, str):
                    logging.error("Wrong filename: '%s'!", type(filename))
                elif os.path.isdir(filename):
                    try:
                        for dirname, subdirs, files in os.walk(filename):
                            zf_out.write(dirname)
                            logging.debug(
                                "Add dir '%s' to '%s'.",
                                dirname,
                                path
                            )
                            for file in files:
                                filepath = os.path.join(dirname, file)
                                zf_out.write(filepath)
                                count_files += 1
                                logging.debug(
                                    "Add file '%s' to '%s'.",
                                    filepath,
                                    path
                                )
                    except BaseException as err:
                        logging.error("'%s' wasn't added!\n%s", filename, err)
                elif os.path.exists(filename):
                    try:
                        zf_out.write(filename)
                        count_files += 1
                        logging.debug("Add file '%s' to '%s'.", filename, path)
                    except tarfile.TarError as err:
                        logging.error("'%s' wasn't added!\n%s", filename, err)
                else:
                    logging.warning("File isn't exists: '%s'.", filename)
        return count_files

    @staticmethod
    def _to_tar(path: str, *files, mode: str="w") -> int:
        count_files = 0
        with tarfile.open(path, mode) as tar_fout:
            for filename in files:
                if not isinstance(filename, str):
                    logging.error("Wrong filename: '%s'!", type(filename))
                elif os.path.exists(filename):
                    try:
                        tar_fout.add(filename)
                        count_files += 1
                        logging.debug("Add file '%s' to '%s'.", filename, path)
                    except tarfile.TarError as err:
                        logging.error("'%s' wasn't added!\n%s", filename, err)
                else:
                    logging.warning("File isn't exists: '%s'.", filename)
        return count_files

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
            logging.debug(
                "'%s' archiving detected [without compression].",
                method
            )

        params = {
            'method': method[0],
            'destination': destination,
            'rewrite': rewrite
        }

        if compression:
            logging.debug(
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

        return Compressor._archive(*filenames, **params)

    @staticmethod
    def _extract(path: str, destination: str=".", **kwargs) -> int:
        # TODO: implement extraction
        # Note: this function signature refer to public method
        # but was hidden until method will be finished
        method, compression = path.lower().split('.')[-2:]
        raise NotImplementedError
