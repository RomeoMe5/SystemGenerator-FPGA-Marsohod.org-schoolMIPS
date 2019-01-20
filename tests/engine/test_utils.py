import json
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, Iterable, NoReturn

import pytest

from engine.constants import PATHS
from engine.utils.misc import none_safe, quote
from engine.utils.prepare import Archiver, Loader, convert, create_dirs
from engine.utils.render import ENV, Render, load_template
from tests import (TEST_DIR, free_test_dir, logging, remove_test_dir,
                   use_test_dir)
from tests.engine import (MOCK_CONFIG, MOCK_DIR, MOCK_TEMPL_NAME,
                          _test_static_content, use_mock_loader)


def test_global_paths() -> NoReturn:
    for attr in ("ROOT", "BASE", "STATIC", "TEMPL", "MIPS"):
        assert hasattr(PATHS, attr), "missed path"
        assert os.path.exists(getattr(PATHS, attr)), "path not exist"


def test_none_safe() -> NoReturn:
    def func(*args, **kwargs) -> Iterable[Any]:
        return list(args) + list(kwargs.values())

    with_args_and_kwargs = none_safe()(func)(1, None, a=0, b=None)
    assert None not in with_args_and_kwargs
    assert len(with_args_and_kwargs) == 2, "no missing items"
    assert sum(with_args_and_kwargs) == 1
    with_args_and_kwargs2 = none_safe()(func)(1, None, None, a=0, b=None)
    assert None not in with_args_and_kwargs2
    assert len(with_args_and_kwargs2) == 2, "no missing items"
    assert sum(with_args_and_kwargs2) == 1

    with_args = none_safe(to_kwargs=False)(func)(0, 1, None)
    assert None not in with_args
    assert len(with_args) == 2, "no missing items"
    assert sum(with_args) == 1
    with_args2 = none_safe(to_kwargs=False)(func)(0, 1, None, a=None)
    assert None in with_args2
    assert len(with_args2) == 3

    with_kwargs = none_safe(to_args=False)(func)(a=0, b=1, c=None)
    assert None not in with_kwargs
    assert len(with_kwargs) == 2, "no missing items"
    assert sum(with_kwargs) == 1
    with_kwargs2 = none_safe(to_args=False)(func)(None, a=0, b=1, c=None)
    assert None in with_kwargs2
    assert len(with_kwargs2) == 3, "no missing items"


class TestArchiver:
    def setup_class(self) -> NoReturn:
        self.tmp_dir = TEST_DIR
        self.arch_name = os.path.join(self.tmp_dir, "arch")
        self.files = tuple(os.path.join(self.tmp_dir, d)
                           for d in ("a", "b", "c"))

    @staticmethod
    def create_file(path: str) -> bool:
        logging.debug("Create file: %s", path)
        with open(path, 'wb') as fout:
            pass
        return os.path.exists(path)

    def setup_method(self) -> NoReturn:
        free_test_dir()
        for filepath in self.files:
            assert self.create_file(filepath), "file not created" + filepath

    def teardown_method(self) -> NoReturn:
        remove_test_dir()

    def test__to_zip(self) -> NoReturn:
        assert not Archiver._to_zip(self.arch_name, *self.files), "no errors"
        assert os.path.exists(self.arch_name), "archive isn't exist"

    def test__to_tar(self) -> NoReturn:
        assert not Archiver._to_tar(self.arch_name, *self.files), "no errors"
        assert os.path.exists(self.arch_name), "archive isn't exist"

    def test__archive(self) -> NoReturn:
        assert Archiver._archive(
            *self.files,
            method="x",
            destination=self.arch_name
        ) < 0, "invalid method was accepted"

        tar_kwargs = {
            'method': "tar",
            'destination': self.arch_name + ".tar"
        }
        zip_kwargs = {
            'method': "zip",
            'destination': self.arch_name + ".zip"
        }

        for res in (Archiver._archive(*self.files, **tar_kwargs),
                    Archiver._archive(*self.files, **zip_kwargs)):
            assert not res, "errors occured"
        assert os.path.exists(tar_kwargs['destination']), "archive exists"
        assert os.path.exists(zip_kwargs['destination']), "archive exists"

        for res in (
            Archiver._archive(*self.files, rewrite=True, **tar_kwargs),
            Archiver._archive(*self.files, rewrite=True, **zip_kwargs)
        ):
            assert not res, "errors occured"

        for res in (
            Archiver._archive(*self.files, rewrite=False, **tar_kwargs),
            Archiver._archive(*self.files, rewrite=False, **zip_kwargs)
        ):
            assert res < 0, "file was rewritten"

    def test_to_tar_flow(self) -> NoReturn:
        Archiver.to_tar_flow({fn: fn for fn in self.files}, self.arch_name)
        assert os.path.exists(self.arch_name + ".tar"), "archive not exist"

    def test_archive(self) -> NoReturn:
        zip_name = self.arch_name + ".zip"
        assert not Archiver.archive(zip_name, *self.files), "errors occured"
        assert os.path.exists(zip_name), "archive not exists"
        assert not Archiver.archive(
            zip_name,
            *self.files,
            rewrite=True
        ), "errors occured"
        assert Archiver.archive(
            zip_name,
            *self.files,
            rewrite=False
        ) < 0, "file was rewrited"

        tar_name = self.arch_name + ".tar"
        assert not Archiver.archive(tar_name, *self.files), "error occured"
        assert os.path.exists(tar_name), "can't find archive"
        assert not Archiver.archive(tar_name, *self.files, rewrite=True)
        assert Archiver.archive(tar_name, *self.files, rewrite=False) < 0


def test_convert() -> NoReturn:
    kwargs = {
        'from_path': MOCK_CONFIG,
        'to_fmt': "json"
    }
    end_filenames = (MOCK_CONFIG[:-3] + "json",
                     os.path.join(TEST_DIR, "file.json"))

    with use_test_dir():
        _ = convert(**kwargs)
        _ = convert(to_path=end_filenames[1], **kwargs)
        for filename in end_filenames:
            assert os.path.exists(filename), "file isn't exist"
            with open(filename, "r") as fin:
                _test_static_content(json.load(fin))
            os.remove(filename)
            assert not os.path.exists(filename), "file wasn't removed"


class TestLoader:
    def setup_class(self) -> NoReturn:
        self.path = MOCK_DIR
        self.fullpath = MOCK_CONFIG
        self.filename = "static-board"
        self.fullname = ".".join((self.filename, "yml"))

    def test_load(self) -> NoReturn:
        for res in (Loader.load(self.fullpath, fmt="yml"),
                    Loader.load(self.fullpath)):
            _test_static_content(res)

    def test_load_static(self) -> NoReturn:
        for res in (Loader.load_static(self.fullpath),
                    Loader.load_static(self.filename, self.path),
                    Loader.load_static(self.fullname, self.path)):
            _test_static_content(res)

    def test_get_static_path(self) -> NoReturn:
        def _test_static_path(filename: str) -> NoReturn:
            path = Loader.get_static_path(filename, self.path)
            assert path and isinstance(path, str)
            assert os.path.exists(path)

        for filename in ("__tmp", self.filename + ".tmp"):
            assert Loader.get_static_path(filename, self.path) is None

        _test_static_path(self.filename)
        _test_static_path(self.fullname)
        _test_static_path(self.fullpath)


def test_create_dirs() -> NoReturn:
    with use_test_dir() as test_dir:
        dirs = tuple(os.path.join(test_dir, d) for d in ("a", "b", "c"))
        assert not create_dirs(*dirs), "errors while creating dirs"
        for d in dirs:
            assert os.path.exists(d), "dir isn't exist" + d
        assert create_dirs(*dirs) == 3, "false rewrite"
        assert not create_dirs(*dirs, rewrite=True), "rewrite isn't work"


class TestRender:
    def setup_class(self) -> NoReturn:
        self.config = Loader.load(MOCK_CONFIG)

    @staticmethod
    def _check_rendered(render_res: str, params: dict) -> NoReturn:
        assert render_res and isinstance(render_res, str)
        for val in params.values():
            if not isinstance(val, (dict, list)):
                logging.debug("Check rendered value: %s", val)
                assert val in render_res

    def make_params(self, filetype: str) -> dict:
        params = {'project_name': "test-proj"}
        params.update(self.config[filetype])
        logging.debug("Make params: %s", params)
        return params

    def test__render(self) -> NoReturn:
        with use_mock_loader():
            mock_template = ENV.get_template(MOCK_TEMPL_NAME)
        strings = {
            'a': "LKAJEI_ID(#F)WI#)FJk",
            'b': "lKSJE(#-q-wd--3_W(#J",
            'c': "!(*@(*)#@*&$))OJDSAI"
        }
        res = Render._render(mock_template, **strings)
        for line, string in zip(res.split('\n'), strings.values()):
            assert line == string

    def test_format_date(self) -> NoReturn:
        date = datetime.utcnow()
        f_date = Render.format_date(date, quoted=False, sep=False)
        fq_date = Render.format_date(date, quoted=True, sep=False)
        fs_date = Render.format_date(date, quoted=False, sep=True)
        assert f_date.count("\"") == 0
        assert fq_date.count("\"") == 2
        assert f_date.count(" ") == 2
        assert fs_date.count(" ") == 3

    def test_qpf(self) -> NoReturn:
        params = self.make_params("qpf")
        self._check_rendered(Render.qpf(**params), params)

    def test_qsf(self) -> NoReturn:
        params = self.make_params("qsf")
        self._check_rendered(Render.qsf(**params), params)

    def test_sdc(self) -> NoReturn:
        params = self.make_params("sdc")
        res = Render.sdc(**params)
        assert res and isinstance(res, str)

    def test_v(self) -> NoReturn:
        params = self.make_params("v")
        self._check_rendered(Render.v(**params), params)

    def test_functions(self) -> NoReturn:
        params = self.make_params("func")
        params['a'] = "alO@)IW)IJW)EWJ)FIJ"

        def check_rendered(data: str) -> NoReturn:
            assert data
            assert isinstance(data, str)
            assert params['a'] in data

        with use_mock_loader():
            for res in (Render.functions(name="functions/func", **params),
                        Render.functions(name="functions/func.v.jinja",
                                         fmt=None, **params)):
                check_rendered(res)


def test_load_template() -> NoReturn:
    def func(*args, **kwargs) -> Dict[str, Any]:
        assert "template" in kwargs
        assert "file_type" in kwargs
        kwargs['args'] = args
        return kwargs

    with use_mock_loader():
        res = load_template(path=MOCK_TEMPL_NAME)(func)(a=0)
    assert "a" in res and res['a'] == 0
    assert res['file_type'] == "func", "isn't auto-detected"

    with use_mock_loader():
        res = load_template(path=MOCK_TEMPL_NAME, file_type="v")(func)(b=1)
    assert "b" in res and res['b'] == 1
    assert res['file_type'] == "v", "isn't auto-detected"
