#!/usr/bin/env python


import sys
import logging
import argparse
import users

logger = logging.getLogger()


def generate_user_list(mailing_list, number_of_users, password_length, prefix, fout, at_domain):
    users_list = users.generate_users_list(mailing_list, number_of_users, password_length, prefix, at_domain)
    users.write_users(users_list, fout)


def make_parser():
    description = \
            "Generate a user list, either using a prepared mailing list (--mailing-list)\n" \
            "or autogenerating emails with a specific email domain (--email-domain)"""
    parser = argparse.ArgumentParser(
            description=description, add_help=True, formatter_class=argparse.RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--num-users', metavar="N", default=None,
            help='Number of users (mutually exclusive with --mailing-list)', type=int)
    group.add_argument('-m', '--mailing-list', metavar="FILE", default=None,
            help='File containing list of emails, one per line and one per users (mutually exclusive with --num-users)')
    parser.add_argument('-l', '--password-length', metavar="L", default=6, help='Length of auto-generated passwords', type=int)
    parser.add_argument('-e', '--email-domain', metavar="DOMAIN",
            help="Domain for generated emails (only if you don't specify --mailing-list)")
    parser.add_argument('-o', '--output', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='Output filename (default: stdout)')
    parser.add_argument('-p', '--username-prefix', metavar="PREFIX", default="user-", help='username prefix')
    return parser

def _parse_options(args):
    parser = make_parser()
    options = parser.parse_args(args)

    if options.mailing_list and options.email_domain:
        parser.error("You can't specify both a --mailing-list and an --email-domain")
    elif options.mailing_list is None and options.email_domain is None:
        parser.error("You must specify either a --mailing-list or an --email-domain for email generation")

    return options

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    logging.basicConfig(level=logging.DEBUG)
    options = _parse_options(args)

    mailing_list = None
    if options.mailing_list is not None:
        with open(options.mailing_list, "r") as f:
            mailing_list = [x.strip() for x in f]
            logger.debug("Size of mailing list: %d", len(mailing_list))
        nusers = len(mailing_list)
    elif options.num_users is not None:
        nusers = options.num_users
    else:
        raise RuntimeError("BUG! num users and mailing list both undefined!")

    generate_user_list(mailing_list, nusers, options.password_length, options.username_prefix, options.output, options.email_domain)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(e)
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception(e)
        sys.exit(99)
