import io
import os
import json
from slugify import slugify

mapping_parent = os.path.expanduser("~/.branchdb/mappings")


class RepoMapping(object):
    def __init__(self, repo):
        self.repo = repo
        self.mapping = self._build_mapping()
        self.__changes = False

    def __enter__(self):
        return self

    def __exit__(self):
        if self.__changes is True:
            self._update_mapping()

    def __getitem__(self, key):
        return self.mapping[key]

    def __setitem__(self, key, value):
        self.mapping[key] = value
        self.__changes = True

    def _build_mapping(self):
        file_loc = self._get_mapping_file_loc(self.repo.active_branch.name)
        with io.open(file_loc, "rb") as mapping_file:
            return json.load(mapping_file)

    def _update_mapping(self):
        file_loc = self._get_mapping_file_loc(self.repo.active_branch.name)
        json.dump(self.mapping, file_loc)
        self.__changes = False

    def _get_mapping_file_loc(self, branch_name):
        normalized_branch_name = slugify(branch_name, separator="_")
        file_name = u"{}.json".format(normalized_branch_name)
        return os.path.join(mapping_parent, file_name)
