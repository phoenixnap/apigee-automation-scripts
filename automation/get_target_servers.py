#!/usr/local/bin/python
"""Script to get target server from Apigee"""

import argparse
import zipfile
import io
from requests import Response
from requests import Session

from service import apigee_auth

# Global session used for all requests.
REQUEST = Session()
APIGEE_API_URL = 'https://api.enterprise.apigee.com/v1/organizations/{}/environments/{}'


class TargetServer:
    def __init__(self, organization: str, environment: str, target_server: any):
        self.organization = organization
        self.environment = environment
        self.target_server = target_server

    def __str__(self):
        return f"TargetServer: organization: {self.organization}, environment: {self.environment}, target_server: {self.target_server}"


def get_target_server(org_name: str, env_name: str, target_server_name: str):
    """Retrieves the target server by name of the given organization name and environment name"""

    response = REQUEST.get((APIGEE_API_URL + '/targetservers/{}').format(org_name, env_name, target_server_name))

    if response.status_code != 200:
        raise Exception(print_error(response))

    target_server = response.json()

    return target_server


def exists_env_in_org(org_name: str, env_name: str):
    """Checks if environment exists in organization"""

    response = REQUEST.get(APIGEE_API_URL.format(org_name, env_name))

    return response.status_code == 200


def print_error(response: Response) -> str:
    """Prints the error returned from an API call"""
    return f'Error: {response.status_code} - {response.reason}. \n {response.text}'


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
        '--organizations',
        help='names of the organizations',
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
        help='file location of the query output',
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
    organizations = args.organizations.split(',')
    username = args.username
    password = args.password
    refresh_token = args.refresh_token
    output_path = args.output

    # Retrieve an access token using the refresh token provided. This ensures
    # that we always have a valid access token.
    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    result = []

    for org in organizations:
        for env in environments:
            if not exists_env_in_org(org, env):
                continue

            target_server = get_target_server(org, env, target_server_name)
            result.append(TargetServer(org, env, target_server))

    for r in result:
        print(r)

    z = zipfile.ZipFile(io.BytesIO(result))
    z.extractall(output_path)

    location = output_path + '/' + z.filelist[0].filename
    print('File stored in: {}'.format(location))

    return location


if __name__ == '__main__':
    main()
