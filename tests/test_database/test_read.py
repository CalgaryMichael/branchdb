# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
from branchdb import database, errors
from .. import mocking


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


@mock.patch("branchdb.database.read.git_tools.get_repo")
def test_get_current_database__not_matching(mock_repo, tmp_path):
    content = {
        "master": "branch_master",
        "test1": "branch_test1",
        "test2": "branch_test2",
        "test3": "branch_test3"}
    with mocking.make_temp_mapping_file(tmp_path, content=content):
        mock_repo.return_value = mocking.MockRepo(active_branch_name="bad", project_root=str(tmp_path))

    error = "Unable to retrieve active branch name. Please add a default database to your settings."
    with pytest.raises(errors.ImproperlyConfigured, match=error):
        database.get_current_database()
