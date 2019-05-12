# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class SlugRegistry(object):
    POSTGRESQL = "postgres"

    def register(self, slug, value):
        if hasattr(self, slug):
            raise ValueError("Slug '{}' is already registered")
        setattr(self, slug, value)


SlugType = SlugRegistry()
