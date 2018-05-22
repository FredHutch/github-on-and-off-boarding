# A REST API for on- and off-boarding users to/from our GitHub Organization

This RESTful Flask/Python 3 application can do three things:

1. Tell you if a user is a member of our organization.
2. Invite a user to join our organization.
3. Remove a user from our organization, including all teams that
   are part of the organization.

It's designed to be used in an automated on-boarding/off-boarding workflow.
This would be facilitated by having a field for GitHub username in
Employee Self Service.

**NOTE**: Tasks `2` and `3` above require you to call the service from
the hosts `jamborite` or `gizmo1`. Calling from other hosts will result in an error.

## Running the app

You must set the following environment variables:

Environment variable name | Purpose
------------------------- | -------
`GITHUB_ORG`              | The name of the GitHub organization, presumably `FredHutch`.
`GITHUB_TOKEN`            | A GitHub access token which must have the permissions `admin:org` and `read:user`.

## API

There is a single endpoint (`/`). Different actions are accomplished with
different HTTP verbs:


HTTP verb    |   action
------------ | ----------------
GET          |  determine if user is member of org
DELETE       |  remove user from org (and org teams)
PUT          |  add user to org


### API Documentation

The following examples assume that the application is deployed
at [https://github-offboarding.fhcrc.org/](https://github-offboarding.fhcrc.org/).

They involve a user with the username `foo`. Note that this is the **GitHub**
username, not a HutchNet ID or any other kind of identifier.

### `GET`

Determines if user is a member of the organization.

Example call:

```
curl https://github-offboarding.fhcrc.org/?username=foo
```

Example result:

```json
{
    "status": false
}
```

### `PUT`

Invites the user to join the organization. They will have to accept the
invitation, by clicking a link in an email.

Example call:

```
curl -X PUT https://github-offboarding.fhcrc.org/?username=foo
```

Example result:

```json
{
    "status": true
}
```

### `DELETE`

Removes the user from all teams in the organization and then from the organization
itself.

Example call:


```
curl -X DELETE https://toolbox.fhcrc.org/github-on-off-boarding/?username=foo
```

Example result:

```json
{
    "status": true
}
```
