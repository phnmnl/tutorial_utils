import os
import csv
from notebook.auth import passwd


def generate_password(user_id, length):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(chars[c % len(chars)] for c in os.urandom(length))


def get_hashed_password(password):
    return passwd(passphrase=password)


def read_users(filename):
    users = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users[row['username']] = row
    return users


def write_users(users, fout):
        writer = csv.DictWriter(fout,
                                fieldnames=["uid", "username", "email", "password", "hashed_password"])
        writer.writeheader()
        writer.writerows(users)


def generate_users_list(mailing_list, number_of_users, password_length, prefix, at_domain=None):
    if mailing_list is None and at_domain is None:
        raise ValueError("No mails provided.  You need to provide an email list or a domain with which to compose email addresses")
    if mailing_list is not None and len(mailing_list) != number_of_users:
        raise ValueError("Length of mailing list ({}) doens't match number of users ({})".format(len(mailing_list), number_of_users))

    users = []
    def make_user(n):
        user_id = n + 1
        username = "{0}{1}".format(prefix, str(user_id))
        email = "{}@{}".format(username, at_domain) if mailing_list is None else mailing_list[n]
        password = generate_password(user_id, password_length)
        hashed_password = get_hashed_password(password)
        return {"uid": user_id, "username": username, "email": email,
                "password": password, "hashed_password": hashed_password}

    users = [ make_user(n) for n in range(number_of_users) ]
    return users
