#!/usr/bin/env python


import os
import sys
import csv
import logging
import argparse
import users

logger = logging.getLogger()


def generate_user_list(mailing_list, number_of_users, password_length, prefix, filename):
    users_list = users.generate_users_list(mailing_list, number_of_users, password_length, prefix)
    users.write_users(users_list, filename)


def make_parser():
    parser = argparse.ArgumentParser(add_help=True, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-u', '--users', default=None, dest="nusers", help='Number of users', type=int)
    parser.add_argument('-m', '--mailing-list', default=None, help='Mailing List')
    parser.add_argument('-l', '--password-length', default=6, help='Password length', type=int)
    parser.add_argument('-f', '--filename', default="users-list.csv", help='Output filename')
    parser.add_argument('-p', '--username-prefix', default="user-", help='username prefix')
    return parser


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        args = sys.argv[1:]
        parser = make_parser()
        options = parser.parse_args(args)
        logger.debug(options)

        mailing_list = None
        if options.mailing_list is not None:
            with open(options.mailing_list, "r") as f:
                mailing_list = [x.strip() for x in f.readlines()]
                logger.debug("Size of mailing list: %d", len(mailing_list))

        if options.nusers is None:
            if mailing_list is not None:
                nusers = len(mailing_list)
            else:
                raise Exception("Number of user undefined!!!")
        else:
            nusers = options.nusers

        generate_user_list(mailing_list, nusers, options.password_length, options.username_prefix, options.filename)
    except Exception as e:
        logger.error(e)
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception(e)
        sys.exit(99)
