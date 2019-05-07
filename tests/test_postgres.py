# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import mock
from psycopg2.sql import Composed, Identifier, SQL
from branchdb.errors import DatabaseError
from branchdb.engines.postgres import postgres_engine, PostgresEngine
from .mocking import mock_postgres_cursor, MockConnection


def test_all_databases():
    engine = PostgresEngine()
    with mock.patch.object(engine, "get_cursor") as mock_cursor:
        mock_cursor.return_value.__enter__ = mock_postgres_cursor([["db1"], ["db2"]])
        result = engine.all_databases()
    assert result == ["db1", "db2"]


@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine._execute")
@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine.database_exists")
def test_create_database(mock_exists, mock_execute):
    mock_exists.return_value = False
    engine = PostgresEngine()
    engine.connection = MockConnection()

    with mock.patch.object(engine, "get_cursor") as mock_cursor:
        cursor = mock_postgres_cursor()
        mock_cursor.return_value.__enter__ = cursor
        result = engine.create_database("jazz", template=None)

    composed_create = Composed([
        SQL("CREATE DATABASE "),
        Identifier("jazz"),
        SQL("\n")])
    mock_execute.assert_any_call(mock.ANY, composed_create)

    composed_grant = Composed([
        SQL("GRANT ALL PRIVILEGES ON DATABASE "),
        Identifier("jazz"),
        SQL(" TO "),
        Identifier("user"),
        SQL("\n")])
    mock_execute.assert_any_call(mock.ANY, composed_grant)
    assert result is True


@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine._execute")
@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine.database_exists")
def test_create_database__with_template(mock_exists, mock_execute):
    mock_exists.return_value = False
    engine = PostgresEngine()
    engine.connection = MockConnection()

    with mock.patch.object(engine, "get_cursor") as mock_cursor:
        cursor = mock_postgres_cursor()
        mock_cursor.return_value.__enter__ = cursor
        result = engine.create_database("jazz2", template="jazz1")

    composed_create = Composed([
        SQL("CREATE DATABASE "),
        Identifier("jazz2"),
        SQL(" TEMPLATE "),
        Identifier("jazz1"),
        SQL("\n")])
    mock_execute.assert_any_call(mock.ANY, composed_create)

    composed_grant = Composed([
        SQL("GRANT ALL PRIVILEGES ON DATABASE "),
        Identifier("jazz2"),
        SQL(" TO "),
        Identifier("user"),
        SQL("\n")])
    mock_execute.assert_any_call(mock.ANY, composed_grant)
    assert result is True


@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine.database_exists")
def test_create_database__existing(mock_exists):
    mock_exists.return_value = True
    engine = PostgresEngine()
    with pytest.raises(DatabaseError, match="Database 'jazz' already exists."):
        engine.create_database("jazz")


@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine._execute")
@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine.database_exists")
def test_delete_database(mock_exists, mock_execute):
    mock_exists.return_value = True
    engine = PostgresEngine()
    engine.connection = MockConnection()

    with mock.patch.object(engine, "get_cursor") as mock_cursor:
        cursor = mock_postgres_cursor()
        mock_cursor.return_value.__enter__ = cursor
        result = engine.delete_database("jazz")

    composed_delete = Composed([
        SQL("DROP DATABASE "),
        Identifier("jazz"),
        SQL("\n")])
    mock_execute.assert_any_call(mock.ANY, composed_delete)
    assert result is True


@mock.patch("branchdb.engines.postgres.postgres_engine.PostgresEngine.database_exists")
def test_delete_database__existing(mock_exists):
    mock_exists.return_value = False
    engine = PostgresEngine()
    with pytest.raises(DatabaseError, match="Database 'jazz' does not exist."):
        engine.delete_database("jazz")
