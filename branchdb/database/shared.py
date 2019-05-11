# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from branchdb import errors
from branchdb.conf import settings
from branchdb.engines import get_engine

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
