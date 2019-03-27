# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from branchdb import git_tools, errors, utils
from . import default_settings


def project_settings_module():
    """Returns the path for the project's personal settings.py file"""
    project_root = git_tools.get_project_root()
    settings_path = os.path.join(project_root, ".branchdb", "settings.py")
    if os.path.exists(settings_path) is False:
        raise errors.ImproperlyConfigured("Unable to find settings module for project")
    return settings_path


class LazySettings(object):
    """Adapted version of django.conf.LazySettings"""

    def __init__(self):
        self._wrapped = None

    def __getattr__(self, key):
        if self._wrapped is None:
            self._setup()
        value = getattr(self._wrapped, key)
        self.__dict__[key] = value
        return value

    def __setattr__(self, key, value):
        if key == "_wrapped":
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is None:
                self._setup()
            setattr(self, key, value)

    def _setup(self):
        settings_module = project_settings_module()
        self._wrapped = Settings(settings_module)

    @property
    def configured(self):
        return self._wrapped is not None


class Settings(object):
    def __init__(self, settings_module):
        self.settings_module = settings_module
        custom_settings = utils.import_source_file("settings", self.settings_module)

        # Note: the ordering matters here
        self._load(default_settings)
        self._load(custom_settings)

    def _load(self, mod):
        for setting in dir(mod):
            if setting.isupper():
                value = getattr(mod, setting)
                setattr(self, setting, value)

    def __repr__(self):
        return "<{cls} \"{module}\">".format(
            cls=self.__class__.__name__,
            module=self.settings_module)


settings = LazySettings()
