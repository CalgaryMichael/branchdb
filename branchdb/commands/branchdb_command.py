# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import shutil
import argparse
from branchdb import database, git_tools, utils, repo_mapping


def main():
    parser = argparse.ArgumentParser(description="Control your branchdb setup for the current project")
    parser.set_defaults(parser=None)
    subparsers = parser.add_subparsers(help="commands")

    # tools parser
    tools_parser = subparsers.add_parser(
        "tools",
        help="General tools to retrieve information about branchdb environment")
    tools_parser.set_defaults(parser="tools")
    tools_parser.add_argument(
        "--current",
        action="store_true",
        default=False,
        help="Get the name of the current database")
    tools_parser.add_argument(
        "--set",
        default=None,
        help="Set a branch to use the specified database (use with '--branch' to point to a specific branch)")
    tools_parser.add_argument(
        "--branch",
        default=None,
        help="Specify a branch to do a paired action on (use with '--set')")

    # init parser
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize your project to be used with the branchdb tool")
    init_parser.set_defaults(parser="init")
    init_parser.add_argument(
        "starting-database",
        help="The starting database for your project.")
    init_parser.add_argument(
        "-e", "--empty",
        action="store_true",
        default=False,
        help="Create a project with am empty settings file.")

    # create parser
    create_parser = subparsers.add_parser(
        "create",
        help="Create new databases based off your git information")
    create_parser.set_defaults(parser="create")
    create_parser.add_argument(
        "-b", "--branch",
        default=None,
        help="The name of the branch you would like to create databases for (default: current branch)")
    create_parser.add_argument(
        "-t", "--template-branch",
        default=None,
        help="The name of the branch you would like to template the new databases from")
    create_parser.add_argument(
        "-T", "--template-database",
        default=None,
        help="The name of the database you would like to template the new databases from")

    # delete parser
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete databases that are associated with your git information")
    delete_parser.set_defaults(parser="delete")
    delete_parser.add_argument(
        "-b", "--branch",
        default=None,
        help="The name of the branch you would like to delete databases for (default: current branch)")
    delete_parser.add_argument(
        "-c", "--clean",
        action="store_true",
        default=False,
        help="Delete databases associated with stale git branches.")
    delete_parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Delete all databases associated with branchdb project.")

    args = parser.parse_args()
    if args.parser == "tools":
        run_tools_command(args)
    if args.parser == "init":
        run_init_command(args)
    elif args.parser == "create":
        run_create_command(args)
    elif args.parser == "delete":
        run_delete_command(args)


def run_tools_command(args):
    if args.current is True:
        print(database.get_current_database())
    if args.set is not None:
        active_branch, project_root = git_tools.get_branch_and_root()
        branch = args.branch or active_branch
        with repo_mapping.RepoMapping(project_root) as mapping:
            mapping[branch] = args.set
        print("Set branch '{}' to point to '{}'".format(branch, args.set))


def run_init_command(args):
    project_root = git_tools.get_project_root()
    local_settings_path = os.path.join(project_root, ".branchdb")
    if os.path.exists(local_settings_path):
        if os.path.exists(os.path.join(local_settings_path, "settings.py")):
            raise Exception("Project is already initialized.")
    else:
        os.mkdir(local_settings_path)
    if args.empty:
        io.open(os.path.join(local_settings_path, "settings.py"), "wb").close()
        utils.json_dump({}, os.path.join(local_settings_path, "mappings.json"))
    else:
        example_path = os.path.join(os.path.dirname(__file__), "data", "settings.example.py")
        settings_path = os.path.join(local_settings_path, "settings.py")
        shutil.copyfile(example_path, settings_path)
        with io.open(settings_path, "a+") as settings_file:
            settings_file.write("DEFAULT_DATABASE_NAME = \"{}\"\n".format(args.starting_database))
        utils.json_dump({}, os.path.join(local_settings_path, "mappings.json"))
    print("Project initialized. Please edit your settings for the database connections.")


def run_create_command(args, dry_run=False):
    repo = git_tools.get_repo()
    branch_name = args.branch or repo.active_branch.name

    msg = "Please only use '--template-branch' or '--template-database'"
    assert bool(args.template_branch and args.template_database) is False, msg
    template = args.template_database or None
    if args.template_branch:
        project_root = git_tools.get_project_root(repo)
        with repo_mapping.RepoMapping(project_root) as mapping:
            template = mapping[args.template_branch]

    try:
        result = database.create_databases(
            branch_name,
            template=template,
            dry_run=dry_run)
    except Exception as e:
        print(e)
        print("Unable to create databases.")
    else:
        if result.success == result.total:
            print("Successfully created '{}' database{}".format(result.success, "" if result.success == 1 else "s"))
        else:
            print("Unable to create all databases.")


def run_delete_command(args):
    repo = git_tools.get_repo()
    if args.all:
        database.delete_all_databases()
        return

    if args.branch is not None or (args.branch is None and args.clean is False):
        branch_name = args.branch or repo.active_branch.name
        try:
            result = database.delete_databases(branch_name)
        except Exception:
            print("Unable to delete databases")
        else:
            if result.success == result.total:
                print("Successfully deleted '{}' database{}".format(result.success, "" if result.success == 1 else "s"))
            else:
                print("Unable to delete all databases.")

    if args.clean is True:
        try:
            result = database.clean_databases()
        except Exception:
            print("Unable to clean databases")
        else:
            if result.success == result.total:
                print("Successfully cleaned '{}' database{}".format(result.success, "" if result.success == 1 else "s"))
            else:
                print("Unable to clean all databases.")


if __name__ == "__main__":
    main()
