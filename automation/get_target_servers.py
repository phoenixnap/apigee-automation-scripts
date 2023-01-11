#!/usr/local/bin/python
"""Script to get target server from Apigee"""

import json
import argparse
import gzip
import os
from pathlib import Path
from requests import Session
from service import apigee_auth, apigee_target_servers

# Global session used for all requests.
REQUEST = Session()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='Gets target server by name from Apigee')
    req_grp = parser.add_argument_group(title='required arguments')
    req_grp.add_argument(
        '-tsn',
        '--target_server_name',
        help='name of the target server',
        required=True)
    req_grp.add_argument(
        '-env',
        '--environments',
        help='names of the environments',
        required=True)
    req_grp.add_argument(
        '-org',
        '--organization',
        help='names of the organization',
        required=True)
    req_grp.add_argument(
        '-u',
        '--username',
        help='apigee user')
    req_grp.add_argument(
        '-pwd',
        '--password',
        help='apigee password')
    req_grp.add_argument(
        '-rt',
        '--refresh_token',
        help='apigee refresh token')
    req_grp.add_argument(
        '-out',
        '--output',
        help='file location of the api result output',
        required=False)
    req_grp.add_argument(
        '-f',
        '--file',
        help='name of the file to store result in',
        required=False)

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error("the following arguments are required: -u/--username and -pwd/--password OR -r/--refresh_token")

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    target_server_name = args.target_server_name
    environments = args.environments.split(',')
    organization = args.organization
    username = args.username
    password = args.password
    refresh_token = args.refresh_token
    output_path = args.output
    file = args.file

    if output_path is None:
        output_path = os.getcwd()
    else:
        Path(output_path).mkdir(parents=True, exist_ok=True)

    if file is None:
        file = 'target-servers.json.gz'

    if not file.endswith('.json.gz'):
        file = file + '.json.gz'

    location = output_path + '/' + file

    # Retrieve an access token using the refresh token provided. This ensures
    # that we always have a valid access token.
    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    result = []

    for env in environments:
        target_server = apigee_target_servers.get_target_server(REQUEST, organization, env, target_server_name)
        if target_server is not None:
            result.append({'environment': env, 'target_server': target_server})

    json_data = json.dumps(result)
    binary_data = json_data.encode()

    with gzip.open(location, 'w') as fout:
        fout.write(binary_data)

    print('File stored in: {}'.format(location))
    return location


if __name__ == '__main__':
    main()
