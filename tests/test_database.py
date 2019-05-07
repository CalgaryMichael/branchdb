# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import mock
import pytest
from branchdb import database
from branchdb.conf import settings
from branchdb.engines.postgres import PostgresEngine
from . import mocking, data_folder

project_root = os.path.join(data_folder, u"mock_project_root")
mock_db_info = [
    {
        "ENGINE": "mock",
        "TEMPLATE": "test_template",
        "USER": "user1",
        "PASSWORD": "password1",
        "HOST": "localhost",
        "PORT": "8001"
    },
    {
        "ENGINE": "mock",
        "USER": "user2",
        "PASSWORD": "password2",
        "HOST": "localhost",
        "PORT": "8002"
    }]


@mock.patch("branchdb.database.git_tools.get_branch_and_root")
def test_get_current_branch_name(mock_branch_root):
    mock_branch_root.return_value = "test", project_root
    db_name = database.get_current_database(dry_run=True)
    assert db_name == "branch_test"


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
def test_get_database_connections():
    connections = list(database.get_database_connections())

    assert str(connections[0][0]) == "<MockEngine unconnected>"
    expected_connect = dict(user="user1", password="password1", host="localhost", port="8001")
    assert connections[0][1] == expected_connect
    assert connections[0][2] == mock_db_info[0]

    assert str(connections[1][0]) == "<MockEngine unconnected>"
    expected_connect = dict(user="user2", password="password2", host="localhost", port="8002")
    assert connections[1][1] == expected_connect
    assert connections[1][2] == mock_db_info[1]


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database.git_tools.get_project_root", return_value=project_root)
@mock.patch("branchdb.engines.base_engine.BaseEngine.create_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_create_databases(mock_connect, mock_create, *args):
    mock_connect.side_effect = [True, True]
    mock_create.side_effect = [True, True]

    database.create_databases("jazz", dry_run=True)
    assert mock_connect.call_count == 2
    assert mock_create.call_count == 2

    expected_calls = [
        mock.call("branch_jazz", template="test_template"),
        mock.call("branch_jazz", template=None)]
    mock_create.assert_has_calls(expected_calls)


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database.git_tools.get_project_root", return_value=project_root)
@mock.patch("branchdb.engines.base_engine.BaseEngine.create_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_create_databases__bad_connect(mock_connect, mock_create, *args):
    mock_connect.side_effect = [True, Exception()]
    mock_create.side_effect = [True, True]

    database.create_databases("jazz", dry_run=True)
    assert mock_connect.call_count == 2
    assert mock_create.call_count == 1


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database.git_tools.get_project_root", return_value=project_root)
@mock.patch("branchdb.engines.base_engine.BaseEngine.create_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_create_databases__bad_create(mock_connect, mock_create, *args):
    mock_connect.side_effect = [True, True]
    mock_create.side_effect = [Exception(), True]

    database.create_databases("jazz", dry_run=True)
    assert mock_connect.call_count == 2
    assert mock_create.call_count == 2


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database.git_tools.get_project_root", return_value=project_root)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases(mock_connect, mock_delete, *args):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [True, True]

    database.delete_databases("jazz")
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 2


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database.git_tools.get_project_root", return_value=project_root)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__not_in_mapping(mock_connect, mock_delete, *args):
    with pytest.raises(Exception, match="No database registered for branch 'bad'"):
        database.delete_databases("bad")
    assert mock_connect.called is False
    assert mock_delete.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database.git_tools.get_project_root", return_value=project_root)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__bad_connect(mock_connect, mock_delete, *args):
    mock_connect.side_effect = [True, Exception()]
    mock_delete.side_effect = [True, True]

    database.delete_databases("jazz")
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 1


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database.git_tools.get_project_root", return_value=project_root)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__bad_delete(mock_connect, mock_delete, *args):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [Exception(), True]

    database.delete_databases("jazz")
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 2
