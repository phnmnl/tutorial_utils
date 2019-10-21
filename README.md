

# Barely documented utility scripts for PhenoMeNal practical sessions

A set of scripts originally created for CloudMET 2017.  Feel free to use,
improve, document, etc.


Original author: Marco Enrico Piras (kikkomep)


## generate_users_list

Generate a user list, either using a prepared mailing list (--mailing-list)
or autogenerating emails with a specific email domain (--email-domain)

### Example

```
./generate_users_list.py -n 5 --email-domain me.com
uid,username,email,password,hashed_password
1,user-1,user-1@me.com,54PRFF,sha1:2311389bb0a3:9e20465e3fcd92ca0e29905653fd99e2abbe852d
2,user-2,user-2@me.com,N4GHV7,sha1:b951e801d670:3336be7879a185e45f0eb44857e1353e696af3a2
3,user-3,user-3@me.com,FYNW3B,sha1:726b54553906:fbd3b3cb90355e375acdf80a2fb6c3b5b7136bf8
4,user-4,user-4@me.com,B9QRE5,sha1:887d84b3f2e6:1dbb2d22e5c4a6160da45c9019f83e3752a763f8
5,user-5,user-5@me.com,7FSGZU,sha1:1329f733043c:b7484370afea3791e8890260ed85cfd0f81a3dd9
```

### Options

```
  -h, --help            show this help message and exit
  -n N, --num-users N   Number of users (mutually exclusive with --mailing-list)
  -m FILE, --mailing-list FILE
                        File containing list of emails, one per line and one per users (mutually exclusive with --num-users)
  -l L, --password-length L
                        Length of auto-generated passwords
  -e DOMAIN, --email-domain DOMAIN
                        Domain for generated emails (only if you don't specify --mailing-list)
  -o [OUTPUT], --output [OUTPUT]
                        Output filename (default: stdout)
  -p PREFIX, --username-prefix PREFIX
```

## galaxy_user_manager

Script to create or delete users from a Galaxy instance.

### Commands

| register   | Create Galaxy users.  You must provide a list of users to create with --users-file  |
| delete     | Delete Galaxy users.  You must provide a list of galaxy users to delete with --galaxy-users-file  |
| delete-all | Delete all Galaxy users |


### Examples

#### Register some users

```
./galaxy_users_manager.py register --server http://192.168.99.100:30700 --api-key 5a16034a792cd4489e1db67930e46b6a  --users-file users_list.csv --output-file galaxy-users.csv
```

The output file has the same data as the input plus new columns containing the galaxy ids.

#### Delete those users

```
./galaxy_users_manager.py delete --server http://192.168.99.100:30700 --api-key 5a16034a792cd4489e1db67930e46b6a --galaxy-users-file galaxy-users.csv
```

Note that Galaxy won't really delete the accounts (the purge functionality isn't
implemented yet).  This means that you won't be able to create accounts with
the same id/email address as old accounts that have been deleted.



#### All in one step

At least on linux, you can do this

```
./generate_users_list.py -n 5 --email-domain me.com | \
  ./galaxy_users_manager.py register --server http://192.168.99.100:30700 --api-key 5a16034a792cd4489e1db67930e46b6a \
     --users-file /dev/stdin --output-file galaxy-users.csv
```

And minimalistic printing works with (the second `" "` is a tab-stop):

`cut -d "," -f 3,5 galaxy-users.csv | tr "," " " | while read A ; do echo "$A" ; echo ; done | lpr `

## Installation / dependencies

Note that `python3-bioblend (0.7.0-2)` from Ubuntu 18.04 is too old, 
`bioblend-0.13.0` is known to work.


