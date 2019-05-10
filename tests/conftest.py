# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import pytest
import mock
from . import data_folder, mocking


@pytest.fixture(scope="session", autouse=True)
def mock_project():
    project_root = os.path.join(data_folder, "mock_project_root")
    mock_repo = mocking.MockRepo(active_branch_name="test", project_root=project_root)
    with mock.patch("branchdb.git_tools.get_repo", return_value=mock_repo) as _fixture:
        yield _fixture
