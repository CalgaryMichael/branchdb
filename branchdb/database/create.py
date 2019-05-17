# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from branchdb import git_tools, repo_mapping, utils
from branchdb.conf import settings
from . import get_database_connections, ExecutionResult


def create_databases(branch_name, template=None, dry_run=False):
    """Create a database for the given git branch across all connections"""
    project_root = git_tools.get_project_root()
    db_name = utils.get_database_name(branch_name)
    success = len(settings.DATABASES)
    for engine, db_info in get_database_connections():
        _template = template or db_info.get("TEMPLATE", settings.DATABASE_TEMPLATE)
        try:
            engine.create_database(db_name, template=_template)
        except Exception as e:
            print(e)
            success -= 1
            continue
    with repo_mapping.RepoMapping(project_root) as mapping:
        mapping.get_or_create(branch_name, dry_run=dry_run)
    return ExecutionResult(success=success, total=len(settings.DATABASES))
