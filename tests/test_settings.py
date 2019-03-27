# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import mock
import pytest
from branchdb import conf, errors
from . import data_folder


@mock.patch("branchdb.conf.os.path.exists")
@mock.patch("branchdb.conf.git_tools.get_project_root")
def test_project_settings_module__found(mock_root, mock_exists):
    root = os.path.join(data_folder, "mock_project_root")
    mock_root.return_value = root
    mock_exists.return_value = True

    settings_module = conf.project_settings_module()
    assert settings_module == os.path.join(root, ".branchdb", "settings.py")


@mock.patch("branchdb.conf.os.path.exists")
@mock.patch("branchdb.conf.git_tools.get_project_root")
def test_project_settings_module__not_found(mock_root, mock_exists):
    root = os.path.join(data_folder, "mock_project_root")
    mock_root.return_value = root
    mock_exists.return_value = False

    with pytest.raises(errors.ImproperlyConfigured):
        conf.project_settings_module()


@mock.patch("branchdb.conf.project_settings_module")
def test_lazy_settings__cache(mock_root):
    path_to_settings = ("mock_project_root", ".branchdb", "settings.py")
    mock_root.return_value = os.path.join(data_folder, *path_to_settings)

    settings = conf.LazySettings()
    assert mock_root.called is False
    assert settings._wrapped is None

    assert len(settings.__dict__) == 1
    assert "DATABASES" not in settings.__dict__

    getattr(settings, "DATABASES")
    assert mock_root.called is True
    assert type(settings._wrapped) is conf.Settings

    assert len(settings.__dict__) == 2
    assert "DATABASES" in settings.__dict__

    # does not call `_setup()` if it has cached results
    mock_root.reset_mock()
    getattr(settings, "DATABASES")
    assert mock_root.called is False


def test_lazy_settings__configured():
    settings = conf.LazySettings()
    assert settings._wrapped is None
    assert settings.configured is False

    settings._wrapped = object()
    assert settings.configured is True


def test_settings__ordering():
    """Prove that we favor the settings of the passed in module over the default settings"""
    settings_module = os.path.join(data_folder, "mock_project_root", ".branchdb", "settings.py")
    settings = conf.Settings(settings_module)
    assert conf.default_settings.AUTO_CREATE is True
    assert settings.AUTO_CREATE is False
    assert settings.NAME_SCHEME == conf.default_settings.NAME_SCHEME
