import io
import os
from typing import NoReturn

import pytest

from engine.boards import BOARDS, Board, GenericBoard
from tests import TEST_DIR, free_test_dir
from tests.engine import MOCK_CONFIG, get_event_loop


class TestGenericBoard(object):
    def setup_class(self) -> NoReturn:
        self.tmp_dir = TEST_DIR
        self.conf_path = MOCK_CONFIG
        self.message = "This is test board configuration"
        self.p_name = "tmp"
        self.res_path = os.path.join(self.tmp_dir, self.p_name)

    def setup_method(self) -> NoReturn:
        self.board = GenericBoard(self.conf_path, message=self.message)

    def teardown_method(self) -> NoReturn:
        free_test_dir()

    def test_GenericBoard(self) -> NoReturn:
        with pytest.raises(AttributeError):
            self.board.__dict__  # has no dict as __slots__
        assert self.board.__slots__

    # NOTE due to bug with passing params
    def test_project_name(self) -> NoReturn:
        for name in [self.p_name, [self.p_name], [[self.p_name]]]:
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
        del self.board._sdc, self.board._qpf, self.board._qsf, self.board._v, \
            self.board._func, self.board._functions, self.board._misc
        self.board.reset()
        for attr in ["_sdc", "_qpf", "_qsf", "_v",
                     "_func", "_functions", "_misc"]:
            assert hasattr(self.board, attr)

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
        with get_event_loop():
            with pytest.raises(AttributeError):
                self.board.dump()
        self.board.generate().dump(self.res_path)
        assert os.path.exists(self.res_path)
        for filename in self.board.configs:
            assert os.path.exists(os.path.join(self.res_path, filename))

    def test_archive(self) -> NoReturn:
        with pytest.raises(AttributeError):
            self.board.archive()
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
