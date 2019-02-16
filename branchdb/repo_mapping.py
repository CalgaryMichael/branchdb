# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import json
from branchdb import utils


class RepoMapping(object):
    __mapping_file_location = None

    def __init__(self, project_root):
        self.project_root = project_root
        self.mapping = self._build_mapping()
        self.__changes = False

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self.__changes is True:
            self._update_mapping()

    def __getitem__(self, key):
        return self.mapping[key]

    def __setitem__(self, key, value):
        self.mapping[key] = value
        self.__changes = True

    @property
    def mapping_file_location(self):
        if self.__mapping_file_location is None:
            branchdb_folder = os.path.join(self.project_root, ".branchdb")
            if os.path.exists(branchdb_folder) is False:
                os.makedirs(branchdb_folder)
            self.__mapping_file_location = os.path.join(branchdb_folder, "mappings.json")
        return self.__mapping_file_location

    def _build_mapping(self):
        if os.path.exists(self.mapping_file_location) is False:
            return {}
        with io.open(self.mapping_file_location, "rb") as mapping_file:
            return json.load(mapping_file)

    def _update_mapping(self):
        utils.json_dump(self.mapping, self.mapping_file_location)
        self.__changes = False
