# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import git_tools, repo_mapping


def get_current_database(dry_run=False):
    """Get the name of the database for the active branch"""
    current_branch, project_root = git_tools.get_branch_and_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get_or_create(current_branch, dry_run=dry_run)
    return db_name


def create_database(branch_name, engine):
    """Creates a database for the given git branch"""
    project_root = git_tools.get_project_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get_or_create(branch_name)
    return engine.create_database(db_name)


def delete_database(branch_name, engine):
    """Delete the database for the associated branch"""
    project_root = git_tools.get_project_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        try:
            db_name = mapping[branch_name]
        except KeyError:
            raise Exception("No database registered for branch '{}'".format(branch_name))
    return engine.delete_database(db_name)


def clean_databases(engine=None):
    """Delete all databases with stale branches"""
    pass
