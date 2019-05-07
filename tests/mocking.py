# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import mock
from decorator import decorator
from branchdb.engines import BaseEngine


@decorator
def monkey_patch(func, o=None, k=None, v=None, *args, **kwargs):
    assert o is not None and k is not None and v is not None
    og = getattr(o, k)
    setattr(o, k, v)
    func(*args, **kwargs)
    setattr(o, k, og)


class MockBranch(object):
    def __init__(self, name):
        self.name = name


class MockRepo(object):
    def __init__(self, active_branch_name):
        self.active_branch_name = active_branch_name

    @property
    def active_branch(self):
        return MockBranch(self.active_branch_name)


def mock_postgres_cursor(fetchall_return=None):
    class MockCursor(object):
        def __init__(self, *args, **kwargs):
            pass

        def execute(self, *args, **kwargs):
            pass

        def fetchall(self, *args, **kwargs):
            return fetchall_return

    return MockCursor


class MockConnectionInfo(object):
    username = "user"


class MockConnection(object):
    def __init__(self, *args, **kwargs):
        self.info = MockConnectionInfo()

    def commit(self, *args, **kwargs):
        pass

    def rollback(self, *args, **kwargs):
        pass


class MockEngine(BaseEngine):
    slug = "mock"
    connection = None
