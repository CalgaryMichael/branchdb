# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import re
import json
import pytest
import mock
from mock import PropertyMock
from contextlib import contextmanager
from branchdb.conf import settings
from branchdb.repo_mapping import RepoMapping
from branchdb import utils
from . import data_folder

project_root = os.path.join(data_folder, u"mock_project_root")


@contextmanager
def make_temp_mapping_file(content=None):
    if content is None:
        content = {}
    mapping_parent = os.path.join(project_root, u".branchdb")
    if not os.path.exists(mapping_parent):
        os.makedirs(mapping_parent)
    file_loc = os.path.join(mapping_parent, u"mappings.json")

    utils.json_dump(content, file_loc)
    with io.open(file_loc, u"rb") as file_:
        yield file_
    os.remove(file_loc)


def test_getitem():
    mapping = RepoMapping(project_root, build=False)
    with pytest.raises(KeyError):
        mapping[u"jazz"]  # not in mapping
    mapping.mapping = {u"test": u"branch_test"}
    assert mapping[u"test"] == u"branch_test"


def test_setitem():
    mapping = RepoMapping(project_root, build=False)
    assert mapping._changes is False
    mapping[u"test"] = u"branch_test"
    assert mapping.mapping == {u"test": u"branch_test"}
    assert mapping._changes is True


@mock.patch(u"branchdb.repo_mapping.RepoMapping._update_mapping")
def test_as_context(mock_update):
    with RepoMapping(project_root, build=False) as mapping:
        assert mapping._changes is False
        mapping["test"] = "branch_test"
        assert mapping._changes is True
    assert mock_update.called is True


@mock.patch(u"branchdb.repo_mapping.RepoMapping._update_mapping")
def test_as_context__no_update(mock_update):
    with RepoMapping(project_root, build=False) as mapping:
        assert mapping._changes is False
    assert mock_update.called is False


@mock.patch(u"branchdb.repo_mapping.os.makedirs")
@mock.patch(u"branchdb.repo_mapping.os.path.exists")
def test_mapping_file_location__no_branchdb_folder(mock_exists, mock_make):
    mock_exists.return_value = False

    mapping = RepoMapping(project_root, build=False)
    file_loc = mapping.mapping_file_location
    expected = r".*\/.branchdb\/mappings\.json"
    assert bool(re.match(expected, file_loc)) is True
    assert mock_exists.called is True
    assert mock_make.called is True


@mock.patch(u"branchdb.repo_mapping.os.makedirs")
@mock.patch(u"branchdb.repo_mapping.os.path.exists")
def test_mapping_file_location__matching_file(mock_exists, mock_make):
    mock_exists.return_value = True
    expected = r".*\/.branchdb\/mappings\.json"

    mapping = RepoMapping(project_root, build=False)
    with make_temp_mapping_file({u"master": u"branch_master"}):
        file_loc = mapping.mapping_file_location
    assert bool(re.match(expected, file_loc)) is True
    assert mock_exists.called is True
    assert mock_make.called is False


@mock.patch(u"branchdb.repo_mapping.os.path.exists")
def test_mapping_file_location__cache_location(mock_exists):
    mock_exists.return_value = True
    expected = r".*\/.branchdb\/mappings\.json"

    mapping = RepoMapping(project_root, build=False)
    with make_temp_mapping_file({u"master": u"branch_master"}):
        file_loc = mapping.mapping_file_location
    assert bool(re.match(expected, file_loc)) is True
    assert mock_exists.called is True

    mock_exists.reset_mock()
    file_loc = mapping.mapping_file_location
    assert bool(re.match(expected, file_loc)) is True
    assert mock_exists.called is False


@mock.patch(u"branchdb.repo_mapping.json.load")
@mock.patch(u"branchdb.repo_mapping.os.path.exists")
@mock.patch(u"branchdb.repo_mapping.RepoMapping.mapping_file_location", new_callable=PropertyMock)
def test_build_mapping__path_does_not_exist(mock_loc, mock_exists, mock_load):
    mock_exists.return_value = False
    mock_loc.return_value = u"/example/mapping.json"

    repo_mapping = RepoMapping(project_root, build=False)
    mapping = repo_mapping._build_mapping()
    assert mapping == {}
    assert mock_load.called is False


@mock.patch(u"branchdb.repo_mapping.os.path.exists")
@mock.patch(u"branchdb.repo_mapping.RepoMapping.mapping_file_location", new_callable=PropertyMock)
def test_build_mapping__path_exist(mock_loc, mock_exists):
    mock_exists.return_value = True
    mock_loc.return_value = os.path.join(data_folder, u"mappings.json")

    repo_mapping = RepoMapping(project_root, build=False)
    mapping = repo_mapping._build_mapping()
    assert mapping == {u"master": u"branch_master", u"test": u"branch_test"}


@mock.patch(u"branchdb.repo_mapping.utils.json_dump")
@mock.patch(u"branchdb.repo_mapping.RepoMapping.mapping_file_location", new_callable=PropertyMock)
def test_update_mapping(mock_loc, mock_dump):
    mock_loc.return_value = u"/example/mapping.json"

    repo_mapping = RepoMapping(project_root, build=False)
    repo_mapping.mapping = {u"master": u"branch_master"}
    repo_mapping._changes = True

    repo_mapping._update_mapping()
    mock_dump.assert_called_with({u"master": u"branch_master"}, u"/example/mapping.json")
    assert repo_mapping._changes is False


def test_get_or_create__existing_branch():
    repo_mapping = RepoMapping(project_root, build=False)
    repo_mapping.mapping = {u"master": u"branch_master"}
    db_name = repo_mapping.get_or_create(u"master")
    assert db_name == "branch_master"
    assert repo_mapping.mapping == {u"master": u"branch_master"}


def test_get_or_create__new_branch():
    repo_mapping = RepoMapping(project_root, build=False)
    repo_mapping.mapping = {u"master": u"branch_master"}
    db_name = repo_mapping.get_or_create(u"test")
    assert db_name == "branch_test"
    assert repo_mapping.mapping == {u"master": u"branch_master", u"test": u"branch_test"}


def test_get_or_create__new_branch__dry_run():
    repo_mapping = RepoMapping(project_root, build=False)
    repo_mapping.mapping = {u"master": u"branch_master"}
    db_name = repo_mapping.get_or_create(u"test", dry_run=True)
    assert db_name == "branch_test"
    assert repo_mapping.mapping == {u"master": u"branch_master"}


def test_get_db_name():
    repo_mapping = RepoMapping(project_root, build=False)
    settings.NAME_SEPARATOR = "-"
    db_name = repo_mapping._get_db_name(u"test")
    assert db_name == "branch-test"
