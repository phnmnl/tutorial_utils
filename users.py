import os
import csv
from notebook.auth import passwd


def generate_password(user_id, length):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(chars[ord(c) % len(chars)] for c in os.urandom(length))


def get_hashed_password(password):
    return passwd(passphrase=password)


def read_users(filename):
    users = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users[row['username']] = row
    return users


def write_users(users, filename):
    with open(os.path.join(filename), "w") as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=["uid", "username", "email", "password", "hashed_password"])
        writer.writeheader()
        writer.writerows(users)


def generate_users_list(mailing_list, number_of_users, password_length, prefix):
    users = []
    for n in range(number_of_users):
        user_id = n + 1
        username = "{0}{1}".format(prefix, str(user_id))
        email = "{}@cloudmet17.crs4.it".format(username) if mailing_list is None else mailing_list[n]
        password = generate_password(user_id, password_length)
        hashed_password = get_hashed_password(password)
        user = {"uid": user_id, "username": username, "email": email,
                "password": password, "hashed_password": hashed_password}

        # add instance to the list of instances
        users.append(user)
    return users
