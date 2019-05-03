# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os.path
import psycopg2.sql
from contextlib import contextmanager
from branchdb.errors import DatabaseError
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
    for key, value in kwargs.items():
        composed_kwargs[key] = psycopg2.sql.Identifier(value)
    return psycopg2.sql.SQL(command).format(*composed_args, **composed_kwargs)


class PostgresEngine(BaseEngine):
    slug = "postgres"
    connection = None

    def connect(self, username=None, password=None, host="localhost", port=""):
        self.connection = psycopg2.connect(user=username, password=password, host=host, port=port)
        return self.connection

    @contextmanager
    def get_cursor(self):
        if self.connection is None:
            raise DatabaseError("Must call 'PostgresEngine.connect()' before retrieving a cursor")
        cursor = self.connection.cursor()
        yield cursor
        cursor.close()

    def disconnect(self):
        return self.connection.close()

    def all_databases(self):
        databases = list()
        with self.get_cursor() as cursor:
            command = get_command("all_databases")
            self._execute(cursor, command)
            for row in cursor.fetchall():
                databases.append(row[0])
        return databases

    def _execute(self, cursor, command):
        try:
            cursor.execute(command)
        except Exception as e:
            self.connection.rollback()
            raise e

    def create_database(self, database_name):
        if self.database_exists(database_name) is True:
            raise DatabaseError("Database '{}' already exists.".format(database_name))
        command = get_command("create_database", database=database_name, template="null")
        with self.get_cursor() as cursor:
            self._execute(cursor, command)
            privileges = get_command(
                "grant_privileges",
                database=database_name,
                user=self.connection.info.username)
            self._execute(cursor, privileges)
            self.connection.commit()
        return True

    def delete_database(self, database_name):
        if self.database_exists(database_name) is False:
            raise DatabaseError("Database '{}' does not exist.".format(database_name))
        command = get_command("delete_database", database=database_name)
        with self.get_cursor() as cursor:
            self._execute(cursor, command)
            self.connection.commit()
        return True
