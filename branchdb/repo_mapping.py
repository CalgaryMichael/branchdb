# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import json
from slugify import slugify
from branchdb import utils
from branchdb.conf import settings


class RepoMapping(object):
    __mapping_file_location = None

    def __init__(self, project_root, build=True):
        self.project_root = project_root
        self.mapping = self._build_mapping() if build is True else {}
        self._changes = False

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self._changes is True:
            self._update_mapping()

    def __getitem__(self, key):
        return self.mapping[key]

    def __setitem__(self, key, value):
        self.mapping[key] = value
        self._changes = True

    def __iter__(self):
        for k, v in self.mapping.items():
            yield k, v

    @property
    def branches(self):
        branches = list(self.mapping.keys())
        branches.sort()
        return branches

    @property
    def databases(self):
        databases = list(self.mapping.values())
        databases.sort()
        return databases

    @property
    def mapping_file_location(self):
        """Returns the location of the mapping file of the current project"""
        if self.__mapping_file_location is None:
            branchdb_folder = os.path.join(self.project_root, u".branchdb")
            if os.path.exists(branchdb_folder) is False:
                os.makedirs(branchdb_folder)
            self.__mapping_file_location = os.path.join(branchdb_folder, u"mappings.json")
        return self.__mapping_file_location

    def _build_mapping(self):
        if os.path.exists(self.mapping_file_location) is False:
            return {}
        with io.open(self.mapping_file_location, u"rb") as mapping_file:
            return json.load(mapping_file)

    def _update_mapping(self):
        utils.json_dump(self.mapping, self.mapping_file_location)
        self._changes = False

    def get(self, *args, **kwargs):
        return self.mapping.get(*args, **kwargs)

    def get_or_create(self, branch_name, dry_run=False):
        """Returns the database name for a branch, and saves it to mapping file if none exists"""
        try:
            db_name = self[branch_name]
        except KeyError:
            db_name = self._get_db_name(branch_name)
            if dry_run is False:
                self[branch_name] = db_name
        return db_name

    def _get_db_name(self, branch_name):
        normalized_branch_name = slugify(branch_name, separator=settings.NAME_SEPARATOR)
        return settings.NAME_SCHEME.format(
            prefix=settings.NAME_PREFIX,
            separator=settings.NAME_SEPARATOR,
            branch=normalized_branch_name,
            suffix=settings.NAME_SUFFIX)

    def remove(self, *args):
        """Removes branch from the mapping file"""
        for arg in args:
            if arg in self.mapping:
                del self.mapping[arg]

    def remove_databases(self, *args):
        """Removes branch from the mapping file based off the database name"""
        branches = list()
        for branch, database in self.mapping.items():
            if len(branches) == len(args):
                # we have found all the databases that were requested
                break
            if database in args:
                branches.append(branch)
        self.remove(*branches)
