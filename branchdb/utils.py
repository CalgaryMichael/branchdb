# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json


def json_dump(content, file_loc):
    """Resolve difference between Python2.7 and Python3.7 versions of json.dump"""
    try:
        with io.open(file_loc, u"w") as file_:
            json.dump(content, file_)
    except TypeError:
        with io.open(file_loc, u"wb") as file_:
            json.dump(content, file_)
