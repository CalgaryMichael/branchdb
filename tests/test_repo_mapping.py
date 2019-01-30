import io
import os
import re
import json
import unittest
from unittest import mock
from contextlib import contextmanager
from git import Repo
from branchdb.repo_mapping import RepoMapping, mapping_parent


@contextmanager
def make_temp_mapping_file(file_name, content=None):
    if content is None:
        content = {}
    if not os.path.exists(mapping_parent):
        os.makedirs(mapping_parent)
    file_loc = os.path.join(mapping_parent, file_name)
    with io.open(file_loc, "w") as file_:
        json.dump(content, file_)
    with io.open(file_loc, "rb") as file_:
        yield file_
    os.remove(file_loc)


class RepoMappingTests(unittest.TestCase):
    @mock.patch("branchdb.repo_mapping.RepoMapping._build_mapping")
    def test_get_mapping_file__no_matching_file(self, mock_build):
        mapping = RepoMapping("")
        branch_name = "test-branch-01"
        file_loc = mapping._get_mapping_file_loc(branch_name)
        expected = r".*\/.branchdb\/mappings\/test_branch_01\.json"
        self.assertEqual(bool(re.match(expected, file_loc)), True)

    @mock.patch("branchdb.repo_mapping.RepoMapping._build_mapping")
    def test_get_mapping_file__matching_file(self, mock_build):
        mapping = RepoMapping("")
        branch_name = "test-branch-02"
        with make_temp_mapping_file("branch_02.json"):
            file_loc = mapping._get_mapping_file_loc(branch_name)
        expected = r".*\/.branchdb\/mappings\/test_branch_02\.json"
        self.assertEqual(bool(re.match(expected, file_loc)), True)
