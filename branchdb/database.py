# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import git_tools, repo_mapping


def get_current_database(dry_run=False):
    repo = git_tools.get_repo()
    current_branch = repo.active_branch.name
    project_root = git_tools.get_project_root(repo)
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get_or_create(current_branch, dry_run=dry_run)
    return db_name
