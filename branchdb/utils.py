# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import six
import json
import slugify
try:
    import importlib.util
except ImportError:
    import imp


def json_dump(content, file_loc):
    """Resolve difference between Python2.7 and Python3.7 versions of json.dump"""
    mode = "wb" if six.PY2 else "w"
    with io.open(file_loc, mode) as file_:
        json.dump(content, file_)


def import_source_file(name, path):
    """Returns the imported module from the provided path. Useful for single file imports"""
    if six.PY2:
        return imp.load_source(name, path)
    else:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def get_database_name(branch_name):
    from branchdb.conf import settings
    normalized_branch_name = slugify.slugify(branch_name, separator=settings.NAME_SEPARATOR)
    return settings.NAME_SCHEME.format(
        prefix=settings.NAME_PREFIX,
        separator=settings.NAME_SEPARATOR,
        branch=normalized_branch_name,
        suffix=settings.NAME_SUFFIX)
