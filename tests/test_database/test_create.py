# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
from branchdb import database, errors
from branchdb.conf import settings
from .. import mocking
from . import mock_db_info


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
