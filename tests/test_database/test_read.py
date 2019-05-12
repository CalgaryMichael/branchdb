# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
from branchdb import database, errors
from branchdb.conf import settings
from branchdb.database import read
from .. import mocking

mock_db_info = [
    {"ENGINE": "postgres", "DEFAULT": "master_db"},
    {"ENGINE": "mongodb", "DEFAULT": "master_db2"}]


@mock.patch("branchdb.database.read.git_tools.get_repo")
def test_get_current_database(mock_repo, tmp_path):
    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(active_branch_name="test1", project_root=str(tmp_path))

    db_name = database.get_current_database()
    assert db_name == "branch_test1"


@mock.patch("branchdb.database.read.get_default_database")
@mock.patch("branchdb.database.read.git_tools.get_repo")
def test_get_current_database__default_fallback(mock_repo, mock_default, tmp_path):
    mock_default.return_value = "branch_master"
    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(active_branch_name="test4", project_root=str(tmp_path))

    db_name = database.get_current_database(slug="postgres")
    assert db_name == "branch_master"


@mock.patch("branchdb.database.read.get_default_database")
@mock.patch("branchdb.database.read.git_tools.get_repo")
def test_get_current_database__no_default_fallback(mock_repo, mock_default, tmp_path):
    mock_default.return_value = None
    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(active_branch_name="bad", project_root=str(tmp_path))

    error = "Unable to retrieve active branch name. Please add a default database to your settings."
    with pytest.raises(errors.ImproperlyConfigured, match=error):
        database.get_current_database(slug=None)


@mocking.monkey_patch(o=settings, k="DEFAULT_DATABASE_NAME", v="master_db")
@mock.patch("branchdb.database.read._get_database_for_slug")
def test_get_default_database__no_database_matching_slug(mock_slug):
    mock_slug.return_value = None
    default_database = read.get_default_database("postgres")
    assert default_database == "master_db"


@mocking.monkey_patch(o=settings, k="DEFAULT_DATABASE_NAME", v="master_db")
@mock.patch("branchdb.database.read._get_database_for_slug")
def test_get_default_database__no_default_set_individually(mock_slug):
    mock_slug.return_value = {"ENGINE": "postgres"}
    default_database = read.get_default_database("postgres")
    assert default_database == "master_db"


@mocking.monkey_patch(o=settings, k="DEFAULT_DATABASE_NAME", v="master_db")
@mock.patch("branchdb.database.read._get_database_for_slug")
def test_get_default_database__favors_individually_set_database(mock_slug):
    mock_slug.return_value = {"ENGINE": "postgres", "DEFAULT": "test_db"}
    default_database = read.get_default_database("postgres")
    assert default_database == "test_db"


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
def test_get_database_for_slug():
    database = read._get_database_for_slug("postgres")
    assert database == mock_db_info[0]


@mocking.monkey_patch(o=settings, k="DATABASES", v=mock_db_info)
def test_get_database_for_slug__no_matching_database():
    database = read._get_database_for_slug("sqlite")
    assert database == None
