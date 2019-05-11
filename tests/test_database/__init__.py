# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from .. import data_folder


project_root = os.path.join(data_folder, u"mock_project_root")
mock_db_info = [
    {
        "ENGINE": "mock",
        "TEMPLATE": "test_template",
        "USER": "user1",
        "PASSWORD": "password1",
        "HOST": "localhost",
        "PORT": "8001"
    },
    {
        "ENGINE": "mock",
        "USER": "user2",
        "PASSWORD": "password2",
        "HOST": "localhost",
        "PORT": "8002"
    }]
