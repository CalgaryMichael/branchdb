# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import six

engine_register = {}


def get_engine(slug):
    """Returns the database engine class for a given slug"""
    return engine_register[slug]


class EngineMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        return super(EngineMetaclass, mcs).__new__(mcs, name, bases, attrs)
        slug = attrs.get("slug")
        if slug is None and name.lower().startswith("base") is False:
            raise Exception("Class '{}' must have a slug attribute".format(name))
        if slug in engine_register:
            raise Exception("Class '{}' has conflicting slug of '{}'".format(name, slug))
        engine_register[slug] = mcs


@six.add_metaclass(EngineMetaclass)
class BaseEngine(object):
    slug = None

    def __init__(self):
        self.connetion = None

    @abc.abstractmethod
    def connect(self, username=None, password=None, host="localhost", port=""):
        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def all_databases(self):
        """Returns a list of all database names that currently exist"""
        raise NotImplementedError()

    @abc.abstractmethod
    def create_database(self, database_name):
        raise NotImplementedError()

    @abc.abstractmethod
    def delete_database(self, database_name):
        raise NotImplementedError()

    def database_exists(self, database_name):
        return any(db == database_name for db in self.all_databases())
