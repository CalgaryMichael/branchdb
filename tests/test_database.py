# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import mock
from branchdb import database
from . import mocking, data_folder

project_root = os.path.join(data_folder, u"mock_project_root")


@mock.patch("branchdb.database.git_tools.get_repo")
@mock.patch("branchdb.database.git_tools.get_project_root")
def test_get_current_branch_name(mock_root, mock_repo):
    mock_repo.return_value = mocking.MockRepo(u"test")
    mock_root.return_value = project_root

    db_name = database.get_current_database(dry_run=True)
    assert db_name == "branch_test"
