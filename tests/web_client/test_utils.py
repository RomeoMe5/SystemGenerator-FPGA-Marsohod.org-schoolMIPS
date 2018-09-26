import os
from typing import NoReturn

import pytest

from tests import TEST_DIR, free_test_dir, remove_test_dir
from tests.web_client import (MOCK_DIR, MockModel, commit_or_rollback,
                              create_mock_app, mock_db)
from web_client.utils.misc import URI_MIN_LEN, get_random_str, get_uri
from web_client.utils.serialize import Serializer


class TestMisc(object):
    def test_get_random_str(self) -> NoReturn:
        random_string = get_random_str()
        assert random_string
        assert isinstance(random_string, str)
        assert random_string != get_random_str()
        assert len(get_random_str(n=10)) == 10
        assert get_random_str(n=3, alphabet="a") == "aaa"
        assert not get_random_str(n=0)

    def test_get_uri(self) -> NoReturn:
        with pytest.raises(ValueError):
            _ = get_uri("a", length=URI_MIN_LEN - 1)
        _ = get_uri("a", length=URI_MIN_LEN + 1)
        uri = get_uri("a", length=URI_MIN_LEN)
        assert uri
        assert isinstance(uri, str)
        assert len(uri) == URI_MIN_LEN


class TestBackupableMixin(object):
    def setup_class(self) -> NoReturn:
        self.app = create_mock_app(db=mock_db)
        self.app.app_context().push()
        self.model = MockModel
        self.data = ("d1-;sldfjs", "d2-o4sioks", "d3-2o3if{)")

    def setup_method(self) -> NoReturn:
        mock_db.create_all()

    def teardown_method(self) -> NoReturn:
        mock_db.session.remove()
        mock_db.drop_all()

    def teardown_class(self) -> NoReturn:
        pass  # self.app.app_context().pop()

    def check_db_is_not_damaged(self) -> NoReturn:
        for obj, item in zip(self.model.query.all(), self.data):
            assert obj.data == item

    def test__asdict(self) -> NoReturn:
        for item in self.data:
            mock_db.session.add(self.model(data=item))
        commit_or_rollback(mock_db)
        for obj, item in zip(self.model.query.all(), self.data):
            data = obj._asdict()
            assert data
            assert isinstance(data, dict)
            assert data['data'] == item
            assert data == obj._asdict()
        self.check_db_is_not_damaged()

    def test__fromdict(self) -> NoReturn:
        for n, item in enumerate(self.data, 1):
            mock_db.session.add(self.model()._fromdict({
                'id': n,
                'data': item
            }))
        commit_or_rollback(mock_db)
        self.check_db_is_not_damaged()

    def test_dump(self) -> NoReturn:
        for item in self.data:
            mock_db.session.add(self.model(data=item))
        commit_or_rollback(mock_db)
        dump = self.model.dump()
        assert dump
        assert isinstance(dump, list)
        for data, item in zip(self.model.dump(), self.data):
            assert isinstance(data, dict)
            assert data['data'] == item
        self.check_db_is_not_damaged()

    def test_load(self) -> NoReturn:
        payload = [{'id': n, 'data': item} for n, item in enumerate(self.data)]
        self.model.load(payload)
        commit_or_rollback(mock_db)
        self.check_db_is_not_damaged()


class TestSerializer(object):
    def setup_class(self) -> NoReturn:
        self.app = create_mock_app(db=mock_db)
        self.app.app_context().push()
        self.model = MockModel
        self.data = ("d1-;sldfjs", "d2-o4sioks", "d3-2o3if{)")

    def setup_method(self) -> NoReturn:
        mock_db.create_all()
        free_test_dir()

    def teardown_method(self) -> NoReturn:
        mock_db.session.remove()
        mock_db.drop_all()
        remove_test_dir()

    def teardown_class(self) -> NoReturn:
        pass  # self.app.app_context().pop()

    def test_dump(self) -> NoReturn:
        for item in self.data:
            mock_db.session.add(self.model(data=item))
        commit_or_rollback(mock_db)
        path = os.path.join(TEST_DIR, "dump")

        def check_dumped(*_) -> NoReturn:
            assert os.path.exists(path)
            for obj, item in zip(self.model.query.all(), self.data):
                assert obj.data == item  # check db is not damaged

        check_dumped(Serializer.dump(path, self.model))  # create dump
        check_dumped(Serializer.dump(path, self.model))  # rewrite dump
        os.remove(path)  # recreate dump
        assert not os.path.exists(path)
        check_dumped(Serializer.dump(path, self.model))

    def test_load(self) -> NoReturn:
        mock_dump_path = os.path.join(MOCK_DIR, "dump")
        not_existing_path = mock_dump_path + "123"
        assert not os.path.exists(not_existing_path)

        Serializer.load(not_existing_path, self.model)
        assert not self.model.query.all()

        Serializer.load(mock_dump_path, self.model, db=mock_db)
        for obj, item in zip(self.model.query.all(), self.data):
            assert obj.data == item

    def test_show(self) -> NoReturn:
        mock_dump_path = os.path.join(MOCK_DIR, "dump")
        not_existing_path = mock_dump_path + "123"
        assert not os.path.exists(not_existing_path)

        assert not Serializer.show(not_existing_path)

        payload = Serializer.show(mock_dump_path)
        assert payload
        assert isinstance(payload, list)
        assert len(payload) == 1
        for data, item in zip(payload[0], self.data):
            assert data['data'] == item
