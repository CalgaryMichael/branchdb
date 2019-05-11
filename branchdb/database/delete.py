# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from contextlib import contextmanager
from branchdb import git_tools, repo_mapping
from branchdb.conf import settings
from . import get_database_connections, ExecutionResult


def _delete_databases(engine, db_names):
    success = len(db_names)
    for db_name in db_names:
        try:
            engine.delete_database(db_name)
        except Exception as e:
            print(e)
            success -= 1
            continue
    return success


def delete_all_databases():
    """Deletes every database associated with the current project"""
    repo = git_tools.get_repo()
    project_root = git_tools.get_project_root(repo)
    with repo_mapping.RepoMapping(project_root) as mapping:
        total = len(mapping.databases) * len(settings.DATABASES)
        success = 0
        for engine, _ in get_database_connections():
            try:
                success += _delete_databases(engine, mapping.databases)
            except Exception as e:
                print(e)
                continue
        mapping.remove(*mapping.branches)
    return ExecutionResult(success=success, total=total)


def delete_databases(branch_name):
    """Delete the database for the associated branch across all database connections"""
    project_root = git_tools.get_project_root()
    mapping = repo_mapping.RepoMapping(project_root)
    try:
        db_name = mapping[branch_name]
    except KeyError:
        raise Exception("No database registered for branch '{}'".format(branch_name))
    success = 0
    for engine, _ in get_database_connections():
        try:
            success += _delete_databases(engine, [db_name])
        except Exception as e:
            print(e)
            continue
    mapping.remove(branch_name)
    return ExecutionResult(success=success, total=len(settings.DATABASES))


def clean_databases():
    """Delete all databases with stale branches"""
    success = 0
    with _stale_databases() as stale_databases:
        total = len(stale_databases) * len(settings.DATABASES)
        for engine, _ in get_database_connections():
            try:
                success += _delete_databases(engine, stale_databases)
            except Exception as e:
                print(e)
                continue
    return ExecutionResult(success=success, total=total)


@contextmanager
def _stale_databases():
    repo = git_tools.get_repo()
    project_root = git_tools.get_project_root(repo)
    remote_branches = list(ref.name for ref in repo.remote().refs)
    with repo_mapping.RepoMapping(project_root) as mapping:
        databases = list(v for k, v in mapping if k not in remote_branches)
        yield databases
        mapping.remove_databases(*databases)
