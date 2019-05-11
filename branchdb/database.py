# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from contextlib import contextmanager
from collections import namedtuple
from . import git_tools, repo_mapping, errors
from .conf import settings
from .engines import get_engine

ExecutionResult = namedtuple("ExecutionResult", ["total", "success"])


def get_database_connections():
    """Generator for connecting all databases"""
    engines = list()
    if len(settings.DATABASES) < 1:
        raise errors.ImproperlyConfigured("Please specify at least one database connection in your settings file.")
    for db_info in settings.DATABASES:
        engine = get_engine(db_info["ENGINE"])()
        engine.connect(
            user=db_info["USER"],
            password=db_info["PASSWORD"],
            host=db_info["HOST"],
            port=db_info["PORT"])
        engines.append((engine, db_info))
    for engine, db_info in engines:
        yield engine, db_info


def get_current_database(slug=None):
    """Get the name of the database for the active branch"""
    current_branch, project_root = git_tools.get_branch_and_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get(current_branch)
    if db_name is None:
        error = "Unable to retrieve active branch name. Please add a default database to your settings."
        raise errors.ImproperlyConfigured(error)
    return db_name


def create_databases(branch_name, template=None, dry_run=False):
    """Create a database for the given git branch across all connections"""
    project_root = git_tools.get_project_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get_or_create(branch_name, dry_run=dry_run)
    success = len(settings.DATABASES)
    for engine, db_info in get_database_connections():
        _template = template or db_info.get("TEMPLATE", settings.DATABASE_TEMPLATE)
        try:
            engine.create_database(db_name, template=_template)
        except Exception as e:
            print(e)
            success -= 1
            continue
    return ExecutionResult(success=success, total=len(settings.DATABASES))


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
