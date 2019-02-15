import io
import json


def json_dump(file_loc, content):
    """Resolve difference between Python2.7 and Python3.7 versions of json.dump"""
    try:
        with io.open(file_loc, "w") as file_:
            json.dump(content, file_)
    except TypeError:
        with io.open(file_loc, "wb") as file_:
            json.dump(content, file_)
