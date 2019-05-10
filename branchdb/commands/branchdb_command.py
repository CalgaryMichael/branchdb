# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import shutil
import argparse
from branchdb import database, git_tools, utils


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

    # init parser
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize your project to be used with the branchdb tool")
    init_parser.set_defaults(parser="init")
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
        print(database.get_current_database(dry_run=True))


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
    else:
        example_path = os.path.join(os.path.dirname(__file__), "data", "settings.example.py")
        shutil.copyfile(example_path, os.path.join(local_settings_path, "settings.py"))
    utils.json_dump({}, os.path.join(local_settings_path, "mappings.json"))
    print("Project initialized. Please edit your settings for the database connections.")


def run_create_command(args, dry_run=False):
    repo = git_tools.get_repo()
    branch_name = args.branch or repo.active_branch.name
    try:
        result = database.create_databases(branch_name, dry_run=dry_run)
    except Exception:
        print("Unable to create databases.")
    else:
        if result.success == result.total:
            print("Successfully created '{}' database{}".format(result.success, "" if result.success == 1 else "s"))
        else:
            print("Unable to create all databases.")


def run_delete_command(args):
    repo = git_tools.get_repo()
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
