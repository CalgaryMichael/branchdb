import os
from git import Repo


def get_repo():
    """Returns the Repo of the current directory"""
    call_dir = os.getcwd()
    return Repo(call_dir, search_parent_directories=True)
