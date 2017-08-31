#!/usr/bin/env python3

"""
A RESTful Flask app to add/remove users from
a given GitHub ORGanization (presumably FredHutch).
Set the ORGanization in the environment variable
GITHUB_ORG. Set your GITHUB authentication TOKEN
in GITHUB_TOKEN.

Pass a 'username' parameter to the '/' endpoint
for the following actions:

HTTP verb    |   action
------------------------
GET          |  determine if user is member of ORG
DELETE       |  remove user from ORG
PUT          |  add user to ORG

If app is running at http://localhost:5000/, the following
command lines will work:

# is user foo a member of the ORG?
curl -X GET -d username=foo http://localhost:5000/
# returns {"status": "yes"}

# add user foo - they will get an invite email
curl -X PUT -d username=foo http://localhost:5000/
# returns {"status": "user has been invited"}

# remove user foo from ORG
curl -X DELETE -d username=foo http://localhost:5000/
# returns {"status": "OK"}
"""

# standard library imports
import os
import sys
import time

# third-party imports
import requests
from hammock import Hammock as Github
from flask import Flask
from flask_restful import Resource, Api, reqparse


APP = Flask(__name__) # pylint: disable=invalid-name
API = Api(APP)
GITHUB = Github('https://api.github.com')

TOKEN = os.getenv('GITHUB_TOKEN')
if not TOKEN:
    print("GITHUB_TOKEN not set!")
    sys.exit(1)

HEADERS = {}
HEADERS["Authorization"] = "token {}".format(TOKEN)
HEADERS["Accept"] = "application/vnd.github.hellcat-preview+json"

ORG = os.getenv("GITHUB_ORG")
if not ORG:
    print("GITHUB_ORG not set!")
    sys.exit(1)

def get_paginated_results(url, delay=0.3):
    """
    Handle paginated results transparently, returning them as one list.
    """
    results = requests.get(url, headers=HEADERS)
    if not 'Link' in results.headers:
        return results.json()
    all_results = results.json()
    while True:
        if not 'rel="next"' in results.headers['Link']:
            return all_results
        links = results.headers['Link'].split(",")
        nextpage = [x for x in links if 'rel="next"' in x][0]
        nextpage = nextpage.split(";")[0].replace("<", "").replace(">", "").strip()
        time.sleep(delay)
        results = requests.get(nextpage, headers=HEADERS)
        all_results.extend(results.json())

    return all_results()


class GithubOnOffBoarder(Resource):
    """RESTful class for managing org/team memberships"""

    def get(self): # pylint: disable=no-self-use
        """GET method; query if user is member of ORG"""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            help='GITHUB username to look up',
                            required=True)
        args = parser.parse_args()
        result = GITHUB.orgs(ORG).members(args.username).GET(headers=HEADERS)
        if result.status_code == 204:
            value = "yes"
        elif result.status_code == 404:
            value = "no"
        elif result.status_code == 302:
            value = "you are not an ORGanization member"
        return {'status': value}

    def put(self): # pylint: disable=no-self-use
        """
        PUT method, invite user to ORG.
        They will be invited and their membership state marked
        as 'pending'. When they accept the invite
        their membership state will be changed to 'active'.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            # help='GITHUB username to look up',
                            required=True)
        args = parser.parse_args()
        result = GITHUB.orgs(ORG).memberships(args.username).PUT(headers=HEADERS)
        obj = result.json()
        if 'message' in obj:
            return obj
        if obj['state'] == 'pending':
            value = "user has been invited"
        elif obj['state'] == 'active':
            value = "user is already a member"
        else:
            value = "ERROR"
        return {"status": value}

    def delete(self): # pylint: disable=no-self-use
        """DELETE method, removes user from ORG."""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            # help='GITHUB username to look up',
                            required=True)
        args = parser.parse_args()
        # first look up all teams in the org to see if the
        # user is in any of those teams & needs to be removed from them.
        teams = get_paginated_results(str(GITHUB.orgs(ORG).teams))
        on_teams = []
        # this will do a lot of I/O, but since this is not called very often,
        # it should not hit our rate limit.
        for team in teams:
            result = GITHUB.teams(team['id']).memberships(args['username']).GET(headers=HEADERS)
            # if status code is 200, the user is a member of the team, whether pending,
            # active, or even a team maintainer.
            if result.status_code == 200:
                on_teams.append(team)

        # remove user from teams
        for team in on_teams:
            result = GITHUB.teams(team['id']).memberships(args['username']).DELETE(headers=HEADERS)

        # now remove user from team
        result = GITHUB.orgs(ORG).members(args.username).DELETE(headers=HEADERS)
        if result.status_code == 204:
            value = "OK"
        elif result.status_code == 404:
            value = "not a member or not authenticated"
        else:
            value = "ERROR"
        return {"status": value}

API.add_resource(GithubOnOffBoarder, '/')

# run me with:
# FLASK_DEBUG=True FLASK_APP=app.py flask run
# or simply:
# python3 app.py
if __name__ == '__main__':
    APP.run(debug=True)
