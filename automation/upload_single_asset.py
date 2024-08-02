#!/usr/local/bin/python
"""Script which is used to upload a single asset on the Apigee portal"""
import argparse
import requests

from service import apigee_auth, apigee_portal, apigee_assets

# Global session used for all requests.
REQUEST = requests.Session()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='uploads a theme according to the configured file')
    req_grp = parser.add_argument_group(title='required arguments')
    req_grp.add_argument(
        '-p',
        '--portal',
        help='name of the portal to update',
        required=True)
    req_grp.add_argument(
        '-f',
        '--file',
        help='path of the file to upload',
        required=True)
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
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    portal_name = args.portal
    file = args.file
    org_name = args.org
    username = args.username
    password = args.password
    refresh_token = args.refresh_token

    # Retrieve an access token using the refresh token provided. This ensures
    # that we always have a valid access token.
    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})
    REQUEST.cookies.update({'access_token': access_token})

    # Check portal and add it if not present
    portal = apigee_portal.get_portal(REQUEST, org_name, portal_name)
    apigee_assets.add_remote_asset(REQUEST, portal.id, file)


if __name__ == '__main__':
    main()
