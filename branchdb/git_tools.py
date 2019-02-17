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


def get_project_root(repo):
    return repo.git.rev_parse(u"--show-toplevel")
