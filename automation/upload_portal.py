#!/usr/local/bin/python
"""Script which is used to create or update an Apigee portal"""
import argparse
import requests
import json

from service import apigee_auth, apigee_portal


# Global session used for all requests.
REQUEST = requests.Session()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='uploads a theme according to the configured file')
    req_grp = parser.add_argument_group(title='required arguments')
    req_grp.add_argument(
        '-f',
        '--file',
        help='config file for portal',
        required=True)
    req_grp.add_argument(
        '-p',
        '--portal',
        help='portal name override')
    req_grp.add_argument(
        '-o',
        '--org',
        help='name of the organization',
        required=True)
    req_grp.add_argument(
        '-u',
        '--username',
        help='apigee automation user')
    req_grp.add_argument(
        '-pwd',
        '--password',
        help='apigee automation password')
    req_grp.add_argument(
        '-rt',
        '--refresh_token',
        help='apigee refresh token')

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error("the following arguments are required: -u/--username "
                     "and -pwd/--password OR -r/--refresh_token")

    return parsed


def main():
    """Method called from the main entry point of the script to do the required  logic."""
    args = parse_args()

    config_file = args.file
    org_name = args.org
    username = args.username
    password = args.password
    portal_name = args.portal
    refresh_token = args.refresh_token

    # Retrieve an access token using the refresh token provided. This ensures
    # that we always have a valid access token.
    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'})

    # Auth cookies Fix: copied from upload_portal_documentation.py:206
    REQUEST.cookies.update({'access_token': access_token})

    # Load portal configuration ... add or update it.
    data = open(config_file, 'r', encoding='utf8').read()
    config = json.loads(data)

    # Override if portal name was passed as a switch.
    if portal_name:
        config['name'] = portal_name

    # Get portal and add it if not present
    portal = apigee_portal.add_or_get_portal(REQUEST, org_name, config['name'], config['description'])

    # Update portal description and analytics
    apigee_portal.update_portal(REQUEST, portal, config)


if __name__ == '__main__':
    main()
