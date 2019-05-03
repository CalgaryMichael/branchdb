# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os.path
import psycopg2.sql
from contextlib import contextmanager
from branchdb.engines import BaseEngine


def get_command(command_name, *args, **kwargs):
    command_file = "{}.sql".format(command_name)
    command_path = os.path.join(os.path.dirname(__file__), "commands", command_file)
    with io.open(command_path) as data:
        command = data.read()
    composed_args = tuple()
    for arg in args:
        composed_args += psycopg2.sql.Identifier(arg)
    composed_kwargs = dict()
    for key, value in kwargs:
        composed_kwargs[key] = psycopg2.sql.Identifier(value)
    return psycopg2.sql.SQL(command).format(*composed_args, **composed_kwargs)


class PostgresEngine(BaseEngine):
    slug = "postgres"

    def connect(self, username=None, password=None, host="localhost", port=""):
        self.connection = psycopg2.connect(user=username, password=password, host=host, port=port)
        self.connection.autocommit = True
        return self.connection

    @contextmanager
    def get_cursor(self):
        cursor = self.connection.cursor()
        yield cursor
        cursor.close()

    def disconnect(self):
        return self.connection.close()

    def all_databases(self):
        databases = list()
        with self.get_cursor() as cursor:
            command = get_command("all_databases")
            cursor.execute(command)
            for row in cursor.fetchall():
                databases.append(row[0])
        return databases