# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from branchdb import utils
from branchdb.conf import settings
from . import mocking


@mocking.monkey_patch(o=settings, k="NAME_SEPARATOR", v="-")
def test_get_database_name():
    db_name = utils.get_database_name(u"test")
    assert db_name == "branch-test"
