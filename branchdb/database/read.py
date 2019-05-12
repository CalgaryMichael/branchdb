# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from branchdb import errors, git_tools, repo_mapping
from branchdb.conf import settings


def get_current_database(slug=None):
    """Get the name of the database for the active branch"""
    current_branch, project_root = git_tools.get_branch_and_root()
    default_database = get_default_database(slug)
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get(current_branch, default_database)
    if db_name is None:
        error = "Unable to retrieve active branch name. Please add a default database to your settings."
        raise errors.ImproperlyConfigured(error)
    return db_name


def get_default_database(slug):
    default_database = settings.DEFAULT_DATABASE_NAME
    try:
        default_database = _get_database_for_slug(slug)["DEFAULT"]
    except (TypeError, KeyError):
        default_database = settings.DEFAULT_DATABASE_NAME
    return default_database


def _get_database_for_slug(slug):
    for database in settings.DATABASES:
        if database.get("ENGINE") == slug:
            return database
