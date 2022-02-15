#!/usr/local/bin/python
"""Script which is used to upload an OpenAPI spec to Apigee."""

import argparse

import requests

from service import apigee_auth

# Global session used for all requests.
REQUEST = requests.Session()


class Spec:
    """Class containing details of an Apigee OpenAPI spec."""

    def __init__(self, name: str, spec_id: str, folder_id: int):
        self.name = name
        self.spec_id = spec_id
        self.folder_id = folder_id


class Folder:
    """Class containing a details of an Apigee folder holding 0+ OpenAPI specs."""

    def __init__(self, folder_id: str, specs: []):
        self.folder_id = folder_id
        self.specs = specs


def print_error(response) -> str:
    """Prints the error returned from an API call"""
    return 'Error: {}. \n {}'.format(response.status_code, response.json())


def get_specs_folder(org_name: str) -> Folder:
    """Retrieves the spec folder of the given organization name together
    with the details of the specs if any."""
    response = REQUEST.get(
        'https://apigee.com/dapi/api/organizations/{}/specs/folder/home'.format(org_name))

    if response.status_code != 200:
        raise Exception(print_error(response))

    print('Successfully fetched OpenAPI Specs folder from Apigee.')

    specs = []
    json = response.json()

    for spec in json['contents']:
        specs.append(Spec(spec['name'], spec['id'], spec['folder']))

    return Folder(json['id'], specs)


def spec_exists(spec_name, specs) -> Spec:
    """Checks whether a given spec name already exists in the list of given specs."""
    for spec in specs:
        if spec.name == spec_name:
            return spec
    return None


def create_empty_spec(org_name: str, folder_id: int, spec_name: str) -> Spec:
    """Creates an empty spec file inside Apigee with the given name inside the given folder ID
    for the specified organization name."""
    url = 'https://apigee.com/dapi/api/organizations/{}/specs/doc'.format(
        org_name)
    data = {
        "folder": folder_id,
        "kind": "Doc",
        "name": spec_name
    }
    response = REQUEST.post(url, json=data)

    if response.status_code != 200:
        raise Exception(print_error(response))

    json = response.json()
    print(
        'Successfully created empty OpenAPI spec in Apigee with name: {} and id: {}'.format(
            json['name'],
            json['id']))
    return Spec(json['name'], json['id'], json['folder'])


def update_spec(org_name: str, spec_id: int, spec_path: str):
    """Updates an existing spec file."""
    url = 'https://apigee.com/dapi/api/organizations/{}/specs/doc/{}/content'.format(
        org_name, spec_id)
    with open(spec_path, 'r', encoding='utf8') as file:
        data = file.read()

    response = REQUEST.put(url, data=data.encode('utf-8'))
    if response.status_code != 200:
        raise Exception(print_error(response))

    print('Successfully uploaded OpenAPI spec to Apigee!')


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='uploads an OpenAPI Spec to Apigee')
    req_grp = parser.add_argument_group(title='required arguments')
    req_grp.add_argument(
        '-n',
        '--name',
        help='name of the OpenAPI Spec',
        required=True)
    req_grp.add_argument(
        '-f',
        '--file',
        help='path of the OpenAPI Spec yaml file',
        required=True)
    req_grp.add_argument(
        '-o',
        '--org',
        help='name of the organization',
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

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error("the following arguments are required: -u/--username and -pwd/--password OR -r/--refresh_token")

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    spec_name = args.name
    spec_path = args.file
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

    # Retrieve all the API specs
    folder = get_specs_folder(org_name)

    # Check if there already is an OpenAPI spec with the same name.
    spec = spec_exists(spec_name, folder.specs)

    # Create a new file for the OpenApi spec on Apigee if there isn't an
    # existing one.
    if not spec:
        print('Spec does not exist - creating it on Apigee')
        spec = create_empty_spec(org_name, folder.folder_id, spec_name)

    # Fill the file with the OpenAPI spec.
    update_spec(org_name, spec.spec_id, spec_path)


if __name__ == '__main__':
    main()
