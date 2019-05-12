# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
import six
from branchdb import database, errors
from branchdb.conf import settings
from branchdb.database.delete import _stale_databases
from .. import mocking
from . import mock_db_info


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.repo_mapping.RepoMapping.remove")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
@mock.patch("branchdb.database.delete.git_tools.get_repo")
def test_delete_all_databases(mock_repo, mock_connect, mock_delete, mock_remove, tmp_path):
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
    mock_remove.assert_called_once_with(*list(content.keys()))


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.repo_mapping.RepoMapping.remove")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
@mock.patch("branchdb.database.delete.git_tools.get_repo")
def test_delete_all_databases__bad_connect(mock_repo, mock_connect, mock_delete, mock_remove, tmp_path):
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
    assert mock_remove.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.repo_mapping.RepoMapping.remove")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
@mock.patch("branchdb.database.delete.git_tools.get_repo")
def test_delete_all_databases__bad_delete(mock_repo, mock_connect, mock_delete, mock_remove, tmp_path):
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
    expect_removed = list(content.keys())
    expect_removed.sort()
    mock_remove.assert_called_once_with(*expect_removed)


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.repo_mapping.RepoMapping.remove")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases(mock_connect, mock_delete, mock_remove):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [True, True]

    result = database.delete_databases("jazz")
    assert result.total == 2
    assert result.success == 2
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 2
    mock_remove.assert_called_once_with("jazz")


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.repo_mapping.RepoMapping.remove")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__not_in_mapping(mock_connect, mock_delete, mock_remove):
    with pytest.raises(Exception, match="No database registered for branch 'bad'"):
        database.delete_databases("bad")
    assert mock_connect.called is False
    assert mock_delete.called is False
    assert mock_remove.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.repo_mapping.RepoMapping.remove")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__bad_connect(mock_connect, mock_delete, mock_remove):
    mock_connect.side_effect = [errors.ConnectionError(), True]
    mock_delete.side_effect = [True, True]

    with pytest.raises(errors.ConnectionError):
        result = database.delete_databases("jazz")
    assert mock_delete.called is False
    assert mock_remove.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
@mock.patch("branchdb.repo_mapping.RepoMapping.remove")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_delete_databases__bad_delete(mock_connect, mock_delete, mock_remove):
    mock_connect.side_effect = [True, True]
    mock_delete.side_effect = [Exception(), True]

    result = database.delete_databases("jazz")
    assert result.total == 2
    assert result.success == 1
    assert mock_connect.call_count == 2
    assert mock_delete.call_count == 2
    mock_remove.assert_called_once_with("jazz")


@mocking.monkey_patch(o=settings, k="DATABASES", v=[mock_db_info[0]])
@mock.patch("branchdb.database.delete._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value.__enter__.return_value = ["branch_test1", "branch_test2", "branch_test3"]
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
@mock.patch("branchdb.database.delete._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases__multiple_engines(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value.__enter__.return_value = ["branch_test1", "branch_test2", "branch_test3"]
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
@mock.patch("branchdb.database.delete._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases__bad_connect(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value.__enter__.return_value = ["branch_test1", "branch_test2", "branch_test3"]
    mock_connect.side_effect = errors.ConnectionError()
    mock_delete.side_effect = [True, True, True]

    with pytest.raises(errors.ConnectionError):
        result = database.clean_databases()
    assert mock_delete.called is False


@mocking.monkey_patch(o=settings, k="DATABASES", v=[mock_db_info[0]])
@mock.patch("branchdb.database.delete._stale_databases")
@mock.patch("branchdb.engines.base_engine.BaseEngine.delete_database")
@mock.patch("branchdb.engines.base_engine.BaseEngine.connect")
def test_clean_databases__bad_delete(mock_connect, mock_delete, mock_stale):
    mock_stale.return_value.__enter__.return_value = ["branch_test1", "branch_test2", "branch_test3"]
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


@mock.patch("branchdb.repo_mapping.RepoMapping.remove_databases")
@mock.patch("branchdb.database.delete.git_tools.get_repo")
def test_stale_databases(mock_repo, mock_remove, tmp_path):
    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    refs = [mocking.MockRef("master"), mocking.MockRef("test2")]
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(project_root=str(tmp_path), refs=refs)

    expected = ["branch_test1", "branch_test3"]
    with _stale_databases() as stale_databases:
        matching_databases = (stale in expected for stale in stale_databases)
    assert all(matching_databases) is True
    try:
        mock_remove.assert_called_once_with(*expected)
    except AssertionError as e:
        if six.PY2:
            # sometimes this fails due to inconsistent ordering on PY2
            mock_remove.assert_called_once_with(*reversed(expected))
        else:
            raise e
