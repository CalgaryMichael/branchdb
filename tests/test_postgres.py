# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
from branchdb.engines import postgres, PostgresEngine
from .mocking import mock_path, mock_postgres_cursor


@mock_path("../data", modules=[postgres])
def test_get_command__numbers():
    result = postgres.get_command("mock_command", 1, arg2="test")
    assert result == "SELECT 1 FROM test"


def test_all_databases():
    engine = PostgresEngine()
    with mock.patch.object(engine, "get_cursor") as mock_cursor:
        mock_cursor.return_value.__enter__ = mock_postgres_cursor([["db1"], ["db2"]])
        result = engine.all_databases()
    assert result == ["db1", "db2"]
