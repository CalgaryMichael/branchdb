# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import pytest
import mock
from . import data_folder


@pytest.fixture(scope="session", autouse=True)
def mock_project_location():
    location = os.path.join(data_folder, "mock_project_root")
    with mock.patch("branchdb.git_tools.get_project_root", return_value=location) as _fixture:
        yield _fixture
