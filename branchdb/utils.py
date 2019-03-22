# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import six
import json


def json_dump(content, file_loc):
    """Resolve difference between Python2.7 and Python3.7 versions of json.dump"""
    mode = "wb" if six.PY2 else "w"
    with io.open(file_loc, mode) as file_:
        json.dump(content, file_)
