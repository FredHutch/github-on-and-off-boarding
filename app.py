#!/usr/bin/env python3

"""
A RESTful Flask app to add/remove users from
a given GitHub organization (presumably FredHutch).
Set the organization in the environment variable
GITHUB_ORG. Set your github authentication token
in GITHUB_TOKEN.

Pass a 'username' parameter to the '/' endpoint
for the following actions:

HTTP verb    |   action
------------------------
GET          |  determine if user is member of org
DELETE       |  remove user from org
PUT          |  add user to org

If app is running at http://localhost:5000/, the following
command lines will work:

# is user foo a member of the org?
curl -X GET -d username=foo http://localhost:5000/

# add user foo - they will get an invite email
curl -X PUT -d username=foo http://localhost:5000/

# remove user foo from org
curl -X DELETE -d username=foo http://localhost:5000/

"""

# standard library imports
import os
import sys

# third-party imports
from hammock import Hammock as Github
from flask import Flask
from flask_restful import Resource, Api, reqparse


app = Flask(__name__) # pylint: disable=invalid-name
api = Api(app)  # pylint: disable=invalid-name
github = Github('https://api.github.com')  # pylint: disable=invalid-name

token = os.getenv('GITHUB_TOKEN') # pylint: disable=invalid-name
if not token:
    print("GITHUB_TOKEN not set!")
    sys.exit(1)

headers = {"Authorization": "token {}".format(token)}  # pylint: disable=invalid-name

org = os.getenv("GITHUB_ORG") # pylint: disable=invalid-name
if not org:
    print("GITHUB_ORG not set!")
    sys.exit(1)

class GithubTeamManager(Resource):
    """RESTful class for managing org memberships"""

    def get(self): # pylint: disable=no-self-use
        """GET method; query if user is member of org"""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            help='github username to look up',
                            required=True)
        args = parser.parse_args()
        result = github.orgs(org).members(args.username).GET(headers=headers)
        if result.status_code == 204:
            value = "yes"
        elif result.status_code == 404:
            value = "no"
        elif result.status_code == 302:
            value = "you are not an organization member"
        return {'status': value}

    def put(self): # pylint: disable=no-self-use
        """
        PUT method, invite user to org.
        They will be invited and their membership state marked
        as 'pending'. When they accept the invite
        their membership state will be changed to 'active'.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            # help='github username to look up',
                            required=True)
        args = parser.parse_args()
        result = github.orgs(org).memberships(args.username).PUT(headers=headers)
        print("status code is {}".format(result.status_code))
        obj = result.json()
        if obj['state'] == 'pending':
            value = "user has been invited"
        elif obj['state'] == 'active':
            value = "user is already a member"
        else:
            value = "ERROR"
        return {"status": value}

    def delete(self): # pylint: disable=no-self-use
        """DELETE method, removes user from org."""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            # help='github username to look up',
                            required=True)
        args = parser.parse_args()
        result = github.orgs(org).members(args.username).DELETE(headers=headers)
        if result.status_code == 204:
            value = "OK"
        elif result.status_code == 404:
            value = "not a member or not authenticated"
        else:
            value = "ERROR"
        return {"status": value}

api.add_resource(GithubTeamManager, '/')

if __name__ == '__main__':
    app.run(debug=True)
