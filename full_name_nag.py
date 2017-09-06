#!/usr/bin/env python3

"""
Script to iterate through all members of the
FredHutch GitHub organization and check which users
do not have their full name in their profile.
Notify (by means of @mentioning in a issue) such
users that they need to add their full name,
and that the email address linked to their
GitHub account should be their fredhutch.org email
address.

QUESTION: Since there's no way for us to know what a GitHub
user's email address is, should we contact ALL
members of the FredHutch org and ask them to
make sure the email address linked to their
GitHub account is a fredhutch.org address? FIXME TODO

"""

import app

def nag(user):
    """tell a user to add a full name to their profile"""
    message = """
Dear @{} ,

This is an automated message from FredHutch.

In order to keep better track of
members of the
[FredHutch](https://github.com/orgs/FredHutch/people)
organization on GitHub, we are requiring that all
members have a full name in their GitHub profile.

You do not have a full name in your profile. Please
[edit your profile](https://github.com/settings/profile)
and add your full name.

Additionally, the email address linked to your
GitHub account should be a `fredhutch.org`
(or `fhcrc.org`) address.

Please make these changes as soon as possible.
In future, accounts without a full name set
will be removed from the FredHutch organization
on GitHub until the full name is set.

Thank you!
    """.format(user)
    # TODO:
    # post an issue in a repos
    # put the user's name in the issue title
    # create the repos first:
    # FredHutch/github-organization-compliance (?)


def main():
    """do the work"""
    members_url = str(app.GITHUB.orgs(app.ORG).members)
    members = app.get_paginated_results(members_url)
    for member in members:
        member_full = app.GITHUB.users(member['login']).GET(headers=app.HEADERS).json()
        if not member_full['name']:
            print("no name for {}!".format(member_full['login']))
            nag(member_full['login'])

if __name__ == "__main__":
    main()
