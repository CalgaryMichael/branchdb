# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from git import Repo


def get_repo():
    """Returns the Repo of the current directory"""
    call_dir = os.getcwd()
    return Repo(call_dir, search_parent_directories=True)


def get_project_root(repo=None):
    """Returns the path to the top-level directory of current project"""
    if repo is None:
        repo = get_repo()
    return repo.git.rev_parse(u"--show-toplevel")


def get_branch_and_root():
    """Returns the active branch name and the current project's root path"""
    repo = get_repo()
    root = get_project_root(repo)
    return repo.active_branch.name, root
