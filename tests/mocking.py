# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import mock
import six
import json
from contextlib import contextmanager
from decorator import decorator
from branchdb.engines import BaseEngine


@contextmanager
def make_temp_mapping_file(tmp_path, content=None):
    if content is None:
        content = {}
    d = tmp_path / ".branchdb"
    d.mkdir()
    file_ = d / "mappings.json"
    if six.PY2 is True:
        file_.write_bytes(json.dumps(content))
    else:
        file_.write_text(json.dumps(content))
    yield file_


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


class MockRef(object):
    def __init__(self, name):
        self.name = name


class MockGit(object):
    def __init__(self, project_root):
        self.project_root = project_root

    def rev_parse(self, *args, **kwargs):
        return self.project_root


class MockRemote(object):
    def __init__(self, refs):
        self.refs = refs


class MockRepo(object):
    def __init__(self, active_branch_name=None, project_root=None, refs=None):
        self.active_branch_name = active_branch_name
        self.project_root = project_root
        self.refs = refs or []

    @property
    def active_branch(self):
        return MockBranch(self.active_branch_name)

    @property
    def git(self):
        return MockGit(self.project_root)

    def remote(self, *args, **kwargs):
        return MockRemote(self.refs)


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
