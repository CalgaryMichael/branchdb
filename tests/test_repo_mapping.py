# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import re
import unittest
import mock
from contextlib import contextmanager
from branchdb.repo_mapping import RepoMapping
from branchdb import utils

base = os.path.dirname(__file__)
project_root = os.path.join(base, "data", "mock_project_root")


@contextmanager
def make_temp_mapping_file(content=None):
    if content is None:
        content = {}
    mapping_parent = os.path.join(project_root, ".branchdb")
    if not os.path.exists(mapping_parent):
        os.makedirs(mapping_parent)
    file_loc = os.path.join(mapping_parent, "mappings.json")

    utils.json_dump(content, file_loc)
    with io.open(file_loc, "rb") as file_:
        yield file_
    os.remove(file_loc)


class RepoMappingTests(unittest.TestCase):
    @mock.patch("branchdb.repo_mapping.RepoMapping._build_mapping")
    def test_mapping_file_location__no_matching_file(self, mock_build):
        mapping = RepoMapping(project_root)
        file_loc = mapping.mapping_file_location
        expected = r".*\/.branchdb\/mappings\.json"
        self.assertEqual(bool(re.match(expected, file_loc)), True)

    @mock.patch("branchdb.repo_mapping.RepoMapping._build_mapping")
    def test_mapping_file_location__matching_file(self, mock_build):
        mapping = RepoMapping(project_root)
        with make_temp_mapping_file({"master": "branch_master"}):
            file_loc = mapping.mapping_file_location
        expected = r".*\/.branchdb\/mappings\.json"
        self.assertEqual(bool(re.match(expected, file_loc)), True)
