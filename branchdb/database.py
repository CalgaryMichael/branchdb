# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import git_tools, repo_mapping
from .conf import settings
from .engines import get_engine


def get_database_connections():
    for db_info in settings.DATABASES:
        engine = get_engine(db_info["ENGINE"])()
        connect_kwargs = dict(
            user=db_info["USER"],
            password=db_info["PASSWORD"],
            host=db_info["HOST"],
            port=db_info["PORT"])
        yield engine, connect_kwargs, db_info


def get_current_database(dry_run=False):
    """Get the name of the database for the active branch"""
    current_branch, project_root = git_tools.get_branch_and_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get_or_create(current_branch, dry_run=dry_run)
    return db_name


def create_databases(branch_name, dry_run=False):
    """Create a database for the given git branch across all connections"""
    project_root = git_tools.get_project_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        db_name = mapping.get_or_create(branch_name, dry_run=dry_run)
    for engine, connect_kwargs, db_info in get_database_connections():
        template = db_info.get("TEMPLATE", settings.DATABASE_TEMPLATE)
        try:
            engine.connect(**connect_kwargs)
            engine.create_database(db_name, template=template)
        except Exception:
            continue


def delete_databases(branch_name):
    """Delete the database for the associated branch across all database connections"""
    project_root = git_tools.get_project_root()
    with repo_mapping.RepoMapping(project_root) as mapping:
        try:
            db_name = mapping[branch_name]
        except KeyError:
            raise Exception("No database registered for branch '{}'".format(branch_name))
    for engine, connect_kwargs, _ in get_database_connections():
        try:
            engine.connect(**connect_kwargs)
            _delete_databases(engine, [db_name])
        except Exception:
            continue


def _delete_databases(engine, db_names):
    for db_name in db_names:
        try:
            engine.delete_database(db_name)
        except Exception:
            continue


def clean_databases():
    """Delete all databases with stale branches"""
    stale_databases = _stale_databases()
    for engine, connect_kwargs, _ in get_database_connections():
        try:
            engine.connect(**connect_kwargs)
            _delete_databases(engine, stale_databases)
        except Exception:
            continue


def _stale_databases():
    repo = git_tools.get_repo()
    project_root = git_tools.get_project_root(repo)
    remote_branches = list(ref.name for ref in repo.remote().refs)
    with repo_mapping.RepoMapping(project_root) as repo:
        return list(v for k, v in repo if k not in remote_branches)
