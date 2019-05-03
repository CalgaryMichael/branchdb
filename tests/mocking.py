# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock


def mock_path(new_location, modules=None):
    def wrapped(func):
        def _(*args, **kwargs):
            if modules is None:
                modules = []
            mock_path_object = MockPathObject(new_location)
            mock_paths = []
            for module in modules:
                mock_paths.append(mock.patch.object(module, "os", "path", mock_path_object))
            for mock_path in mock_paths:
                mock_path.start()
            func(*args, **kwargs)
            for mock_path in mock_paths:
                mock_path.stop()
    return wrapped


class MockPathObject(object):
    def __init__(self, location):
        self.location = location

    def dirname(self, *args, **kwargs):
        return self.location


class MockBranch(object):
    def __init__(self, name):
        self.name = name


class MockRepo(object):
    def __init__(self, active_branch_name):
        self.active_branch_name = active_branch_name

    @property
    def active_branch(self):
        return MockBranch(self.active_branch_name)


def mock_postgres_cursor(fetchall_return):
    class MockCursor(mock.Mock):
        def execute(self, *args, **kwargs):
            pass

        def fetchall(self, *args, **kwargs):
            return fetchall_return

    return MockCursor()


class MockEngine(object):
    slug = "mock"

    def connect(self, **kwargs):
        pass

    def disconnect(self):
        pass

    def create_db(self, database_name):
        pass

    def delete_db(self, database_name):
        pass


def create_mock_engine(**kwargs):
    mock_engine = MockEngine()
    assert set(kwargs).issubset(mock_engine.__dict__)

    for key, value in kwargs.items():
        mock_engine[key] = value

    return mock_engine
