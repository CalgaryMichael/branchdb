# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from branchdb import errors, git_tools, repo_mapping


def get_current_database():
    """Get the name of the database for the active branch"""
    current_branch, project_root = git_tools.get_branch_and_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get(current_branch)
    if db_name is None:
        error = "Unable to retrieve active branch name. Please add a default database to your settings."
        raise errors.ImproperlyConfigured(error)
    return db_name
