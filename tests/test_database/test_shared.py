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
