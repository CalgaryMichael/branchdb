# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import pytest
import mock
import six
from branchdb.commands.branchdb_command import (
    run_tools_command, run_init_command,
    run_create_command, run_delete_command)
from . import mocking

command_data_folder = os.path.join(os.path.realpath(".."), "branchdb", "commands", "data")


class Args(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@mock.patch("branchdb.commands.branchdb_command.database.get_current_database")
def test_run_tools_command__current_branch(mock_current):
    run_tools_command(Args(current=False))
    assert mock_current.called is False

    run_tools_command(Args(current=True))
    assert mock_current.called is True


@mock.patch("branchdb.commands.branchdb_command.git_tools.get_project_root")
def test_run_init_command(mock_root, tmp_path):
    with io.open(os.path.join(command_data_folder, "settings.example.py"), "rb") as file_:
        settings_example = file_.read()

    mock_root.return_value = str(tmp_path)
    settings_location = os.path.join(str(tmp_path), ".branchdb", "settings.py")
    mapping_location = os.path.join(str(tmp_path), ".branchdb", "mappings.json")

    assert os.path.exists(settings_location) is False
    assert os.path.exists(mapping_location) is False

    run_init_command(Args(empty=False))
    assert os.path.exists(settings_location) is True
    assert os.path.exists(mapping_location) is True

    with io.open(settings_location, "rb") as file_:
        assert file_.read() == settings_example


@mock.patch("branchdb.commands.branchdb_command.git_tools.get_project_root")
def test_run_init_command__empty(mock_root, tmp_path):
    mock_root.return_value = str(tmp_path)
    settings_location = os.path.join(str(tmp_path), ".branchdb", "settings.py")
    mapping_location = os.path.join(str(tmp_path), ".branchdb", "mappings.json")

    assert os.path.exists(settings_location) is False
    assert os.path.exists(mapping_location) is False

    run_init_command(Args(empty=True))
    assert os.path.exists(settings_location) is True
    assert os.path.exists(mapping_location) is True

    with io.open(settings_location, "rb") as file_:
        assert file_.read() == b""


@mock.patch("branchdb.commands.branchdb_command.git_tools.get_project_root")
def test_run_init_command__existing_setup(mock_root, tmp_path):
    d = tmp_path / ".branchdb"
    d.mkdir()
    file_ = d / "settings.py"
    if six.PY2 is True:
        file_.write_bytes(b"")
    else:
        file_.write_text("")

    mock_root.return_value = str(tmp_path)
    assert os.path.exists(os.path.join(str(tmp_path), ".branchdb", "settings.py")) is True

    with pytest.raises(Exception, match="Project is already initialized."):
        run_init_command(Args(empty=False))


@mock.patch("branchdb.commands.branchdb_command.database.create_databases")
@mock.patch("branchdb.commands.branchdb_command.git_tools.get_repo")
def test_run_create_command(mock_repo, mock_create):
    mock_repo.return_value = mocking.MockRepo(active_branch_name="test")
    run_create_command(Args(branch=None), dry_run=True)
    mock_create.assert_called_with("test", dry_run=True)


@mock.patch("branchdb.commands.branchdb_command.database.create_databases")
@mock.patch("branchdb.commands.branchdb_command.git_tools.get_repo")
def test_run_create_command__specified_branch(mock_repo, mock_create):
    mock_repo.return_value = mocking.MockRepo(active_branch_name="test1")
    run_create_command(Args(branch="test2"), dry_run=True)
    mock_create.assert_called_with("test2", dry_run=True)


@mock.patch("branchdb.commands.branchdb_command.database.clean_databases")
@mock.patch("branchdb.commands.branchdb_command.database.delete_databases")
@mock.patch("branchdb.commands.branchdb_command.git_tools.get_repo")
def test_run_delete_command(mock_repo, mock_delete, mock_clean):
    mock_repo.return_value = mocking.MockRepo(active_branch_name="test")
    run_delete_command(Args(branch=None, clean=False))
    mock_delete.assert_called_with("test")
    assert mock_clean.called is False


@mock.patch("branchdb.commands.branchdb_command.database.clean_databases")
@mock.patch("branchdb.commands.branchdb_command.database.delete_databases")
@mock.patch("branchdb.commands.branchdb_command.git_tools.get_repo")
def test_run_delete_command__specified_branch(mock_repo, mock_delete, mock_clean):
    mock_repo.return_value = mocking.MockRepo(active_branch_name="test1")
    run_delete_command(Args(branch="test2", clean=False))
    mock_delete.assert_called_with("test2")
    assert mock_clean.called is False


@mock.patch("branchdb.commands.branchdb_command.database.clean_databases")
@mock.patch("branchdb.commands.branchdb_command.database.delete_databases")
@mock.patch("branchdb.commands.branchdb_command.git_tools.get_repo")
def test_run_delete_command(mock_repo, mock_delete, mock_clean):
    mock_repo.return_value = mocking.MockRepo(active_branch_name="test")
    run_delete_command(Args(branch=None, clean=True))
    assert mock_delete.called is False
    assert mock_clean.called is True


@mock.patch("branchdb.commands.branchdb_command.database.clean_databases")
@mock.patch("branchdb.commands.branchdb_command.database.delete_databases")
@mock.patch("branchdb.commands.branchdb_command.git_tools.get_repo")
def test_run_delete_command__specified_branch(mock_repo, mock_delete, mock_clean):
    mock_repo.return_value = mocking.MockRepo(active_branch_name="test1")
    run_delete_command(Args(branch="test2", clean=True))
    mock_delete.assert_called_with("test2")
    assert mock_clean.called is True
