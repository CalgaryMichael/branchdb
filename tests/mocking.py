# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

class MockBranch(object):
    def __init__(self, name):
        self.name = name


class MockRepo(object):
    def __init__(self, active_branch_name):
        self.active_branch_name = active_branch_name

    @property
    def active_branch(self):
        return MockBranch(self.active_branch_name)


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
