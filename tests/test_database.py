# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import mock
import pytest
from branchdb import database, errors
from branchdb.conf import settings
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
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_get_database_connections(mock_connect):
    mock_connect.side_effect = [True, True]
    connections = list(database.get_database_connections())
    assert mock_connect.call_count == 2

    assert str(connections[0][0]) == "<MockEngine unconnected>"
    expected_connect = dict(user="user1", password="password1", host="localhost", port="8001")
    assert connections[0][1] == mock_db_info[0]

    assert str(connections[1][0]) == "<MockEngine unconnected>"
    assert connections[1][1] == mock_db_info[1]


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_get_database_connections__bad_connect(mock_connect):
    mock_connect.side_effect = [errors.ConnectionError(), True]
    with pytest.raises(errors.ConnectionError):
        connections = list(database.get_database_connections())


@mocking.monkey_patch(o=settings, k="DATABASES", v=[])
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_get_database_connections__no_databases(mock_connect):
    error = "Please specify at least one database connection in your settings file."
    with pytest.raises(errors.ImproperlyConfigured, match=error):
        connections = list(database.get_database_connections())
    assert mock_connect.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.create_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_create_databases(mock_connect, mock_create):
    mock_connect.side_effect = [True, True]
    mock_create.side_effect = [True, True]

    result = database.create_databases("jazz", dry_run=True)
    assert result.total == 2
    assert result.success == 2
    assert mock_connect.call_count == 2
    assert mock_create.call_count == 2

    expected_calls = [
        mock.call("branch_jazz", template="test_template"),
        mock.call("branch_jazz", template=None)]
    mock_create.assert_has_calls(expected_calls)


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.create_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_create_databases__bad_connect(mock_connect, mock_create):
    mock_connect.side_effect = [errors.ConnectionError(), True]
    mock_create.side_effect = [True, True]

    with pytest.raises(errors.ConnectionError):
        database.create_databases("jazz", dry_run=True)
    assert mock_create.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.create_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_create_databases__bad_create(mock_connect, mock_create):
    mock_connect.side_effect = [True, True]
    mock_create.side_effect = [Exception(), True]

    result = database.create_databases("jazz", dry_run=True)
    assert result.total == 2
    assert result.success == 1
    assert mock_connect.call_count == 2
    assert mock_create.call_count == 2


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
@mock.patch("branchdb.database.git_tools.get_repo")
def test_delete_all_databases(mock_repo, mock_connect, mock_delete, tmp_path):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [True] * 8

    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(project_root=str(tmp_path))

    result = database.delete_all_databases()
    assert result.total == 8
    assert result.success == 8
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 8


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
@mock.patch("branchdb.database.git_tools.get_repo")
def test_delete_all_databases__bad_connect(mock_repo, mock_connect, mock_delete, tmp_path):
    mock_connect.side_effect = [errors.ConnectionError(), True]
    mock_delete.side_effect = [True] * 8

    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(project_root=str(tmp_path))

    with pytest.raises(errors.ConnectionError):
        database.delete_all_databases()
    assert mock_delete.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
@mock.patch("branchdb.database.git_tools.get_repo")
def test_delete_all_databases__bad_delete(mock_repo, mock_connect, mock_delete, tmp_path):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [True, True, True, Exception(), True, True, True, True]

    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(project_root=str(tmp_path))

    result = database.delete_all_databases()
    assert result.total == 8
    assert result.success == 7
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 8


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases(mock_connect, mock_delete):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [True, True]

    result = database.delete_databases("jazz")
    assert result.total == 2
    assert result.success == 2
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 2


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__not_in_mapping(mock_connect, mock_delete):
    with pytest.raises(Exception, match="No database registered for branch 'bad'"):
        database.delete_databases("bad")
    assert mock_connect.called is False
    assert mock_delete.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__bad_connect(mock_connect, mock_delete):
    mock_connect.side_effect = [errors.ConnectionError(), True]
    mock_delete.side_effect = [True, True]

    with pytest.raises(errors.ConnectionError):
        result = database.delete_databases("jazz")
    assert mock_delete.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__bad_delete(mock_connect, mock_delete):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [Exception(), True]

    result = database.delete_databases("jazz")
    assert result.total == 2
    assert result.success == 1
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 2


@mocking.monkey_patch(o=settings, k="DATABASES", v=[mock_db_info[0]])
@mock.patch("branchdb.database._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value = ["branch_test1", "branch_test2", "branch_test3"]
    mock_connect.return_value = True
    mock_delete.side_effect = [True, True, True]

    result = database.clean_databases()
    assert result.total == 3
    assert result.success == 3
    assert mock_connect.call_count == 1
    expected_calls = [
        mock.call("branch_test1"),
        mock.call("branch_test2"),
        mock.call("branch_test3")]
    mock_delete.assert_has_calls(expected_calls)


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.database._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases__multiple_engines(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value = ["branch_test1", "branch_test2", "branch_test3"]
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [True] * 6

    result = database.clean_databases()
    assert result.total == 6
    assert result.success == 6
    assert mock_connect.call_count == 2
    expected_calls = [
        # first engine
        mock.call("branch_test1"),
        mock.call("branch_test2"),
        mock.call("branch_test3"),

        # second engine
        mock.call("branch_test1"),
        mock.call("branch_test2"),
        mock.call("branch_test3")]
    mock_delete.assert_has_calls(expected_calls)


@mocking.monkey_patch(o=settings, k="DATABASES", v=[mock_db_info[0]])
@mock.patch("branchdb.database._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases__bad_connect(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value = ["branch_test1", "branch_test2", "branch_test3"]
    mock_connect.side_effect = errors.ConnectionError()
    mock_delete.side_effect = [True, True, True]

    with pytest.raises(errors.ConnectionError):
        result = database.clean_databases()
    assert mock_delete.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=[mock_db_info[0]])
@mock.patch("branchdb.database._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases__bad_delete(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value = ["branch_test1", "branch_test2", "branch_test3"]
    mock_connect.return_value = True
    mock_delete.side_effect = [True, Exception(), True]

    result = database.clean_databases()
    assert result.total == 3
    assert result.success == 2
    assert mock_connect.call_count == 1
    expected_calls = [
        mock.call("branch_test1"),
        mock.call("branch_test2"),
        mock.call("branch_test3")]
    mock_delete.assert_has_calls(expected_calls)


@mock.patch("branchdb.database.git_tools.get_project_root")
@mock.patch("branchdb.database.git_tools.get_repo")
def test_stale_databases(mock_repo, mock_root, tmp_path):
    mock_root.return_value = str(tmp_path)
    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    refs = [mocking.MockRef("master"), mocking.MockRef("test2")]
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(project_root=str(tmp_path), refs=refs)

    stale_databases = database._stale_databases()
    expected = ["branch_test1", "branch_test3"]
    matching_databases = (stale in expected for stale in stale_databases)
    assert all(matching_databases) is True
