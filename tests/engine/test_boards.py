# [dev] TODO add tests for mips

import io
import os
from typing import NoReturn

import pytest

from engine.boards import BOARDS, Board, GenericBoard
from tests import TEST_DIR, use_test_dir
from tests.engine import MOCK_CONFIG


class TestGenericBoard(object):
    def setup_class(self) -> NoReturn:
        self.conf_path = MOCK_CONFIG
        self.message = "This is test board configuration"
        self.p_name = "tmp"
        self.res_path = os.path.join(TEST_DIR, self.p_name)

    def setup_method(self) -> NoReturn:
        self.board = GenericBoard(self.conf_path, message=self.message)

    def test_GenericBoard(self) -> NoReturn:
        with pytest.raises(AttributeError):
            self.board.__dict__  # has no dict as __slots__
        assert self.board.__slots__

    def test_config_path(self) -> NoReturn:
        assert self.board.config_path == self.conf_path, "invalid configs"
        with pytest.raises(FileNotFoundError):
            self.board.config_path = self.conf_path + ")@!O##K(D"
        assert isinstance(self.board._v, dict), "invalid board configuration"
        v = self.board._v
        self.board._v = None
        self.board.config_path = self.conf_path
        assert self.board._v == v, "board isn't reseted"

    # NOTE due to bug with passing params
    def test_project_name(self) -> NoReturn:
        for name in (self.p_name, (self.p_name,), ((self.p_name,),)):
            self.board.project_name = name
            assert self.board.project_name == self.p_name

    def test_params(self) -> NoReturn:
        assert GenericBoard.Param.items
        assert GenericBoard.Param.type
        params = self.board.params
        assert params
        assert isinstance(params, dict)
        for key, param in params.items():
            assert isinstance(key, str)
            assert isinstance(param, GenericBoard.Param)

    def _test_as_archive(self) -> NoReturn:
        with pytest.raises(AttributeError):
            _ = self.board.as_archive
        res = self.board.generate().as_archive
        assert res
        assert isinstance(res, io.Bytes)

    def test_reset(self) -> NoReturn:
        attributes = ("_sdc", "_qpf", "_qsf", "_v", "_func", "_functions",
                      "_misc", "_mips_qsf", "_mips_v")
        for attr in attributes:
            delattr(self.board, attr)
            assert not hasattr(self.board, attr), "attribute wasn't deleted"
        self.board.reset()
        for attr in attributes:
            assert hasattr(self.board, attr), "attributes isn't reseted"

    # [minor] TODO finish test
    def test_setup(self) -> NoReturn:
        board = self.board.setup()
        assert not hasattr(board, "configs")

    # [minor] TODO add more cases
    def test_generate(self) -> NoReturn:
        def check_generated(board: dict) -> NoReturn:
            assert isinstance(board, GenericBoard)
            assert board.configs
            assert isinstance(board.configs, dict)

        check_generated(self.board.generate())
        check_generated(self.board.generate())
        check_generated(self.board.generate(
            flt={'key': True},
            func={'Seven': True}
        ))
        check_generated(self.board.generate(self.p_name))
        check_generated(self.board.setup().generate())

    def test_dump(self) -> NoReturn:
        with pytest.raises(AttributeError):
            self.board.dump()
        with use_test_dir():
            self.board.generate().dump(self.res_path)
            assert os.path.exists(self.res_path)
            for filename in self.board.configs:
                assert os.path.exists(os.path.join(self.res_path, filename))

    def test_archive(self) -> NoReturn:
        with pytest.raises(AttributeError):
            self.board.archive()
        with use_test_dir():
            self.board.generate().archive(self.res_path)
            assert os.path.exists(self.res_path + ".tar")


class TestBoard(object):
    def test_Board(self) -> NoReturn:
        board = Board(BOARDS[0])
        with pytest.raises(AttributeError):
            board.__dict__  # has no dict as __slots__
        assert board.__slots__
        with pytest.raises(ValueError):
            Board(BOARDS[0] * 2)  # there is no such board
