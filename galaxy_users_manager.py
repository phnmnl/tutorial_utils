#!/usr/bin/env python

from __future__ import print_function


import os as _os
import sys as _sys
import csv as _csv
import logging as _logging
import argparse as _argparse

import users as _users
# bioblend dependencies
from bioblend.galaxy import GalaxyInstance

from future.utils import iteritems as _iteritems

# logging
logger = _logging.getLogger()


# Galaxy ENV variable names
ENV_KEY_GALAXY_URL = "GALAXY_URL"
ENV_KEY_GALAXY_API_KEY = "GALAXY_API_KEY"


# Commands
CMD_Register = "register"
CMD_Delete = "delete"
CMD_DeleteAll = "delete-all"

def get_galaxy_instance(galaxy_url=None, galaxy_api_key=None):
    """
    Private utility function to instantiate and configure a :class:`bioblend.GalaxyInstance`
    :type galaxy_url: str
    :param galaxy_url: the URL of the Galaxy server
    :type galaxy_api_key: str
    :param galaxy_api_key: a registered Galaxy API KEY
    :rtype: :class:`bioblend.GalaxyInstance`
    :return: a new :class:`bioblend.GalaxyInstance` instance
    """
    # configure `galaxy_url`
    if galaxy_url is None:
        if ENV_KEY_GALAXY_URL not in _os.environ:
            raise RuntimeError("Galaxy URL not defined!  Use --server or the environment variable {} "
                               "or specify it in the test configuration".format(ENV_KEY_GALAXY_URL))
        else:
            galaxy_url = _os.environ[ENV_KEY_GALAXY_URL]

    # configure `galaxy_api_key`
    if galaxy_api_key is None:
        if ENV_KEY_GALAXY_API_KEY not in _os.environ:
            raise RuntimeError("Galaxy API key not defined!  Use --api-key or the environment variable {} "
                               "or specify it in the test configuration".format(ENV_KEY_GALAXY_API_KEY))
        else:
            galaxy_api_key = _os.environ[ENV_KEY_GALAXY_API_KEY]

    # initialize the galaxy instance
    return GalaxyInstance(galaxy_url, galaxy_api_key)


def register_users(galaxy_instance, users_list, create_api_key=False, report_filename=None):
    if report_filename:
        if _os.path.exists(report_filename):
            raise ValueError("Output file {} already exists.  Won't overwrite".format(report_filename))
        ofile = open(report_filename, 'w')
    else:
        ofile = _sys.stdout

    try:
        actual_users = {u["email"]: u for u in galaxy_instance.users.get_users()}
        logger.debug("Number of users to register: %d", len(users_list))

        galaxy_users = []  # registered_galaxy_users.values()
        for username, u_data in _iteritems(users_list):
            try:
                if not u_data["email"] in actual_users:
                    logger.debug("Registering user: %s - %s", u_data["username"], u_data["email"])
                    user = galaxy_instance.users.create_local_user(u_data["username"], u_data["email"], u_data["password"])
                    u_data["galaxy_id"] = user["id"]
                    if create_api_key:
                        api_key = galaxy_instance.users.create_user_apikey(user['id'])
                        logger.debug("Create API_KEY %s for user %s", api_key, username)
                        galaxy_users.append({"galaxy_id": user["id"], "uid": u_data["uid"],
                                             "username": u_data["username"], "email": u_data["email"], "api_key": api_key,
                                             "password": u_data["password"], "hashed_password": u_data["hashed_password"]})
                        logger.info("User registered with ID '%s' and API_KEY '%s'", u_data["id"], api_key)
                    else:
                        galaxy_users.append({"galaxy_id": user["id"], "uid": u_data["uid"],
                                             "username": u_data["username"], "email": u_data["email"],
                                             "password": u_data["password"], "hashed_password": u_data["hashed_password"]})
                        logger.info("User registered with ID: %s", user["id"])
            except Exception as e:
                logger.debug(e)

        logger.info("Registered users: %d", len(galaxy_users))
        logger.debug("Writing report to '%s' %d users", report_filename, len(galaxy_users))
        writer = _csv.DictWriter(ofile,
                                 fieldnames=["uid", "galaxy_id", "username", "email", "password", "hashed_password",
                                             "api_key"])
        writer.writeheader()
        writer.writerows(galaxy_users)
    finally:
        if report_filename:
            ofile.close()


def delete_users(galaxy_instance, users):
    logger.debug("Number of users to delete: %d", len(users))
    for _, user in _iteritems(users):
        galaxy_instance.users.delete_user(user["galaxy_id"])
        logger.info("Deleted user %s: %s", user["galaxy_id"], user["email"])


def delete_all_users(galaxy_instance):
    current_user = galaxy_instance.users.get_current_user()
    users = galaxy_instance.users.get_users()
    for user in users:
        if user["galaxy_id"] != current_user["id"]:
            galaxy_instance.users.delete_user(user["galaxy_id"])
            logger.info("Deleted user %s: %s", user["galaxy_id"], user["email"])

def make_parser():
    parser = _argparse.ArgumentParser(add_help=True, formatter_class=_argparse.RawTextHelpFormatter)
    parser.add_argument('--server', default=None, help='Galaxy server URL', dest="galaxy_url")
    parser.add_argument('--api-key', default=None, help='Galaxy server API KEY', dest="galaxy_api_key")
    parser.add_argument('--with-api-access', dest="create_api_key",
                        default=True, action='store_true', help='Enable API access for new users')
    parser.add_argument('-f', '--users-file', metavar="FILE",
            help='User list file (like the one generated by the companion script `generate_users_list.py`)')
    parser.add_argument('-g', '--galaxy-users-file', metavar="FILE",
            help='Galaxy user list file (like the one generated by the {} command in this script)'.format(CMD_Register))
    parser.add_argument('-o', '--output-file', metavar="FILE",
            help='Output file containing defaults of the registered Galaxy users')
    parser.add_argument('cmd', choices=[CMD_Register, CMD_Delete, CMD_DeleteAll], default=CMD_Register,
                        help='Action to perform')
    return parser


def parse_args(args):
        parser = make_parser()
        options = parser.parse_args(args)
        # option validation
        if options.cmd == CMD_Register:
            if not options.users_file:
                parser.error("{}: You must specify a list of users with --users-file".format(options.cmd))
            if not options.output_file:
                parser.error("{}: You must specify an --output-file for the new user data".format(options.cmd))
        elif options.cmd == CMD_Delete and not options.galaxy_users_file:
            parser.error("{}: You must specify a list of galaxy users to delete with --galaxy-users-file".format(options.cmd))
        elif options.cmd == CMD_DeleteAll:
            if options.users_file or options.galaxy_users_file:
                parser.error("{}: You can't specify --users-file or --galaxy-users-file when deleting all users".format(options.cmd))

        if options.cmd == CMD_DeleteAll or options.cmd == CMD_Delete:
            if options.output_file:
                parser.error("{}: You can't specify --output-file when deleting users".format(options.cmd))

        return options

def main(args):
    try:
        _logging.basicConfig(level=_logging.DEBUG)
        if args is None:
            args = sys.argv[1:]
        options = parse_args(args)

        galaxy_instance = get_galaxy_instance(options.galaxy_url, options.galaxy_api_key)

        if options.cmd == CMD_Register:
            users = _users.read_users(options.users_file)
            logger.debug("Number of users to register: %d", len(users))
            register_users(galaxy_instance, users, options.create_api_key, options.output_file)
        elif options.cmd == CMD_Delete:
            users = _users.read_users(options.galaxy_users_file)
            delete_users(galaxy_instance, users)
        elif options.cmd == CMD_DeleteAll:
            delete_all_users(galaxy_instance)
        else:
            raise RuntimeError("BUG!  Got invalid command!")
    except Exception as e:
        logger.error(e)
        if logger.isEnabledFor(_logging.DEBUG):
            logger.exception(e)
        _sys.exit(99)


if __name__ == '__main__':
    main(_sys.argv[1:])
