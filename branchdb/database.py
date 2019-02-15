from slugify import slugify
from . import git_tools, repo_mapping


def get_current_database(**env_kwargs):
    repo = git_tools.get_repo()
    current_branch = repo.active_branch.name
    mapping = repo_mapping.RepoMapping(repo)
    try:
        db_name = mapping[current_branch]
    except KeyError:
        db_name = _get_default_database_name(current_branch)
        mapping[current_branch] = db_name
    return db_name


def _get_default_database_name(branch_name):
    normalized_branch_name = slugify(branch_name, separator="_")
    return u"branch_{}".format(normalized_branch_name)
