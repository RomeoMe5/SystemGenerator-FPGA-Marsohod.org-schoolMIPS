import asyncio
import json
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, Iterable, NoReturn

import pytest

from engine.utils.globals import PATHS
from engine.utils.misc import none_safe
from engine.utils.prepare import Archiver, Convertor, Loader, create_dirs
from engine.utils.render import ENV, Render, load_template
from tests import TEST_DIR, free_test_dir, logging
from tests.engine import (MOCK_CONFIG, MOCK_DIR, MOCK_FUNC_TEMPL_NAME,
                          MOCK_TEMPL_NAME, _test_static_content,
                          get_event_loop, use_mock_loader)


def teardown_module() -> NoReturn:
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    assert not os.path.exists(TEST_DIR)


def test_global_paths() -> NoReturn:
    assert hasattr(PATHS, 'ROOT')
    assert hasattr(PATHS, 'BASE')
    assert hasattr(PATHS, 'STATIC')
    assert hasattr(PATHS, 'TEMPL')


def test_none_safe() -> NoReturn:
    def func(*args, **kwargs) -> Iterable[Any]:
        return list(args) + list(kwargs.values())

    with_args_and_kwargs = none_safe()(func)(1, None, a=0, b=None)
    assert None not in with_args_and_kwargs
    assert len(with_args_and_kwargs) == 2  # no missing items
    assert sum(with_args_and_kwargs) == 1
    with_args_and_kwargs2 = none_safe()(func)(1, None, None, a=0, b=None)
    assert None not in with_args_and_kwargs2
    assert len(with_args_and_kwargs2) == 2  # no missing items
    assert sum(with_args_and_kwargs2) == 1

    with_args = none_safe(to_kwargs=False)(func)(0, 1, None)
    assert None not in with_args
    assert len(with_args) == 2
    assert sum(with_args) == 1
    with_args2 = none_safe(to_kwargs=False)(func)(0, 1, None, a=None)
    assert None in with_args2
    assert len(with_args2) == 3

    with_kwargs = none_safe(to_args=False)(func)(a=0, b=1, c=None)
    assert None not in with_kwargs
    assert len(with_kwargs) == 2
    assert sum(with_kwargs) == 1
    with_kwargs2 = none_safe(to_args=False)(func)(None, a=0, b=1, c=None)
    assert None in with_kwargs2
    assert len(with_kwargs2) == 3


class TestArchiver:
    def setup_class(self) -> NoReturn:
        self.tmp_dir = TEST_DIR
        self.arch_name = os.path.join(self.tmp_dir, "arch")
        self.files = tuple(os.path.join(self.tmp_dir, d)
                           for d in ("a", "b", "c"))
        self.loop = asyncio.new_event_loop()

    @staticmethod
    async def create_file(path: str) -> bool:
        logging.debug("Create file: %s", path)
        with open(path, 'wb') as fout:
            pass
        return os.path.exists(path)

    def setup_method(self) -> NoReturn:
        asyncio.set_event_loop(self.loop)
        tasks = (self.create_file(filepath) for filepath in self.files)
        for res in self.loop.run_until_complete(asyncio.gather(*tasks)):
            assert res

    def teardown_method(self) -> NoReturn:
        free_test_dir()

    def teardown_class(self) -> NoReturn:
        self.loop.close()

    def test__to_zip(self) -> NoReturn:
        assert asyncio.run(Archiver._to_zip(self.arch_name, *self.files)) > 0
        assert os.path.exists(self.arch_name)

    def test__to_tar(self) -> NoReturn:
        assert asyncio.run(Archiver._to_tar(self.arch_name, *self.files)) > 0
        assert os.path.exists(self.arch_name)

    # [minor] BUG can't dispatch class-level event loop
    def test__archive(self) -> NoReturn:
        with pytest.raises(ValueError) as exc:
            asyncio.run(Archiver._archive(
                *self.files,
                method="x",
                destination=self.arch_name
            ))

        tar_kwargs = {
            'method': "tar",
            'destination': self.arch_name + ".tar"
        }
        zip_kwargs = {
            'method': "zip",
            'destination': self.arch_name + ".zip"
        }
        tasks = (
            (Archiver._archive(*self.files, **tar_kwargs),
             Archiver._archive(*self.files, **zip_kwargs)),
            (Archiver._archive(*self.files, rewrite=True, **tar_kwargs),
             Archiver._archive(*self.files, rewrite=True, **zip_kwargs)),
            (Archiver._archive(*self.files, rewrite=False, **tar_kwargs),
             Archiver._archive(*self.files, rewrite=False, **zip_kwargs))
        )

        with get_event_loop() as loop:
            for res in loop.run_until_complete(asyncio.gather(*tasks[0])):
                assert res > 0
            assert os.path.exists(tar_kwargs['destination'])
            assert os.path.exists(zip_kwargs['destination'])

            for r in zip(loop.run_until_complete(asyncio.gather(*tasks[1])),
                        loop.run_until_complete(asyncio.gather(*tasks[2]))):
                assert r[0] > 0
                assert r[1] == -1

    def test_to_tar_flow(self) -> NoReturn:
        files = {fn: fn for fn in self.files}
        res = asyncio.run(Archiver.to_tar_flow(files, self.arch_name))
        assert os.path.exists(self.arch_name + ".tar")

    # [dev][minor] TODO make async as in test__archive
    def test_archive(self) -> NoReturn:
        zip_name = self.arch_name + ".zip"
        assert asyncio.run(Archiver.archive(zip_name, *self.files)) > 0
        assert os.path.exists(zip_name)
        assert asyncio.run(Archiver.archive(
            zip_name,
            *self.files,
            rewrite=True
        )) > 0
        assert asyncio.run(Archiver.archive(
            zip_name,
            *self.files,
            rewrite=False
        )) == -1

        tar_name = self.arch_name + ".tar"
        assert asyncio.run(Archiver.archive(tar_name, *self.files)) > 0
        assert os.path.exists(tar_name)
        assert asyncio.run(Archiver.archive(
            tar_name,
            *self.files,
            rewrite=True
        )) > 0
        assert asyncio.run(Archiver.archive(
            tar_name,
            *self.files,
            rewrite=False
        )) == -1


class TestConvertor:
    def setup_class(self) -> NoReturn:
        self.tmp_dir = TEST_DIR
        self.conf_path = MOCK_CONFIG
        self.fmt = "yml"
        self.loop = asyncio.new_event_loop()

    def setup_method(self) -> NoReturn:
        asyncio.set_event_loop(self.loop)

    def teardown_method(self) -> NoReturn:
        free_test_dir()

    def teardown_class(self) -> NoReturn:
        self.loop.close()

    def test__load_content(self) -> NoReturn:
        tasks = (Convertor._load_content(self.conf_path, fmt=self.fmt),
                 Convertor._load_content(self.conf_path))
        for res in self.loop.run_until_complete(asyncio.gather(*tasks)):
            _test_static_content(res)

    def test_convert(self) -> NoReturn:
        kwargs = {
            'from_path': self.conf_path,
            'to_fmt': "json"
        }

        end_filenames = (self.conf_path[:-3] + "json",
                         os.path.join(self.tmp_dir, "file.json"))
        tasks = (Convertor.convert(**kwargs),
                 Convertor.convert(to_path=end_filenames[1], **kwargs))
        _ = self.loop.run_until_complete(asyncio.gather(*tasks))

        for filename in end_filenames:
            assert os.path.exists(filename)
            with open(filename, "r") as fin:
                _test_static_content(json.load(fin))
            os.remove(filename)
            assert not os.path.exists(filename)


class TestLoader:
    def setup_class(self) -> NoReturn:
        self.path = MOCK_DIR
        self.fullpath = MOCK_CONFIG
        self.filename = "static-board"
        self.fullname = ".".join((self.filename, "yml"))
        self.loop = asyncio.new_event_loop()

    def setup_method(self) -> NoReturn:
        asyncio.set_event_loop(self.loop)

    def teardown_method(self) -> NoReturn:
        free_test_dir()

    def teardown_class(self) -> NoReturn:
        self.loop.close()

    def test_load(self) -> NoReturn:
        _test_static_content(asyncio.run(Loader.load(self.fullpath)))

    def test_load_static(self) -> NoReturn:
        tasks = (Loader.load_static(self.fullpath),
                 Loader.load_static(self.filename, self.path),
                 Loader.load_static(self.fullname, self.path))
        for res in self.loop.run_until_complete(asyncio.gather(*tasks)):
            _test_static_content(res)

    # [minor] BUG can't dispatch class-level event loop
    def test_get_static_path(self) -> NoReturn:
        async def _test_static_path(filename: str) -> NoReturn:
            path = await Loader.get_static_path(filename, self.path)
            assert path and isinstance(path, str)
            assert os.path.exists(path)

        for filename in ("__tmp", self.filename + ".tmp"):
            with pytest.raises(FileNotFoundError) as exc:
                _ = asyncio.run(Loader.get_static_path(filename, self.path))

        tasks = (_test_static_path(self.filename),
                 _test_static_path(self.fullname),
                 _test_static_path(self.fullpath))

        with get_event_loop() as loop:
            _ = loop.run_until_complete(asyncio.gather(*tasks))


def test_create_dirs() -> NoReturn:
    dirs = tuple(os.path.join(TEST_DIR, d) for d in ("a", "b", "c"))
    with get_event_loop():
        assert create_dirs(*dirs) == 0
        for d in dirs:
            assert os.path.exists(d)
        assert create_dirs(*dirs) == 3
        assert create_dirs(*dirs, rewrite=True) == 0
    free_test_dir()


class TestRender:
    def setup_class(self) -> NoReturn:
        self.config = asyncio.run(Loader.load(MOCK_CONFIG))
        self.loop = asyncio.new_event_loop()

    def setup_method(self) -> NoReturn:
        asyncio.set_event_loop(self.loop)

    def teardown_method(self) -> NoReturn:
        free_test_dir()

    def teardown_class(self) -> NoReturn:
        self.loop.close()

    @staticmethod
    def _check_rendered(render_res: str, params: dict) -> NoReturn:
        assert render_res and isinstance(render_res, str)
        for val in params.values():
            if not isinstance(val, (dict, list)):
                assert val in render_res

    def make_params(self, filetype: str) -> dict:
        params = {'project_name': "test-proj"}
        params.update(self.config[filetype])
        return params

    def test__render(self) -> NoReturn:
        with use_mock_loader():
            mock_template = ENV.get_template(MOCK_TEMPL_NAME)
        strings = {
            'a': "LKAJEI_ID(#F)WI#)FJk",
            'b': "lKSJE(#-q-wd--3_W(#J",
            'c': "!(*@(*)#@*&$))OJDSAI"
        }
        res = asyncio.run(Render._render(mock_template, **strings))
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
        params = self.make_params('qpf')
        self._check_rendered(asyncio.run(Render.qpf(**params)), params)

    def test_qsf(self) -> NoReturn:
        params = self.make_params('qsf')
        self._check_rendered(asyncio.run(Render.qsf(**params)), params)

    def test_sdc(self) -> NoReturn:
        params = self.make_params('sdc')
        res = asyncio.run(Render.sdc(**params))
        assert res and isinstance(res, str)

    def test_v(self) -> NoReturn:
        params = self.make_params('v')
        self._check_rendered(asyncio.run(Render.v(**params)), params)

    def test_functions(self) -> NoReturn:
        params = self.make_params('func')
        params['name'] = MOCK_FUNC_TEMPL_NAME
        params['a'] = "alO@)IW)IJW)EWJ)FIJ"
        with use_mock_loader():
            res = asyncio.run(Render.functions(**params))
        assert res and isinstance(res, str)
        assert params['a'] in res


def test_load_template() -> NoReturn:
    def func(*args, **kwargs) -> Dict[str, Any]:
        assert "template" in kwargs
        assert "file_type" in kwargs
        kwargs['args'] = args
        return kwargs

    with use_mock_loader():
        res = load_template(path=MOCK_TEMPL_NAME)(func)(a=0)
    assert "a" in res and res['a'] == 0
    assert res['file_type'] == "func"  # auto-detected

    with use_mock_loader():
        res = load_template(path=MOCK_TEMPL_NAME, file_type="v")(func)(b=1)
    assert "b" in res and res['b'] == 1
    assert res['file_type'] == "v"
