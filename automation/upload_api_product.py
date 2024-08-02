#!/usr/local/bin/python
"""Script to create or update an API Product on Apigee"""

import json
import argparse
import requests

from service import apigee_auth

# Global session used for all requests.
REQUEST = requests.Session()


def print_error(response) -> str:
    """Prints the error returned from an API call."""
    return 'Error: {}. \n {}'.format(response.status_code, response.json())


def product_exists(name: str, org_name: str) -> bool:
    """Checks if a product with the given name already exists in the given Apigee organization."""
    response = REQUEST.get(
        'https://api.enterprise.apigee.com/v1/organizations/{}/apiproducts'.format(org_name))

    if response.status_code != 200:
        print_error(response)
        raise response.raise_for_status()

    for product_name in response.json():
        if product_name == name:
            return True

    return False


def create_api_product(org_name: str, product_json: str):
    """Creates an API Product in Apigee."""
    response = REQUEST.post(
        'https://api.enterprise.apigee.com/v1/organizations/{}/apiproducts'.format(org_name),
        json=product_json)

    if response.status_code != 201:
        print_error(response)
        raise response.raise_for_status()

    print("Successfully created API Product with name '{}'.".format(
        product_json['name']))


def update_api_product(org_name: str, product_json: str):
    """Updates an existing API Product in Apigee"""
    product_name: str = product_json['name']

    response = REQUEST.put(
        'https://api.enterprise.apigee.com/v1/organizations/{}/apiproducts/{}'.format(
            org_name, product_name), json=product_json)

    if response.status_code != 200:
        print_error(response)
        raise response.raise_for_status()

    print("Successfully updated API Product with name '{}'.".format(product_name))


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='creates or updates an API product in Apigee')
    req_grp = parser.add_argument_group(title='required arguments')
    req_grp.add_argument(
        '-f',
        '--file',
        help='path of the API Product JSON file',
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

    product_path = args.file
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

    # Read JSON file containing API Product setup information.
    data = open(product_path, 'r', encoding='utf8').read()
    product = json.loads(data)
    product_name: str = product['name']

    # Name is mandatory in the JSON file, otherwise we would not know
    # whether we want to create or update.
    if 'name' not in product:
        raise IOError(
            print_error('API Product name not specified in JSON file.'))

    exists: bool = product_exists(product_name, org_name)

    if exists:
        print("API Product with name '{}' already exists. Performing an update."
              .format(product_name))
        update_api_product(org_name, product)
    else:
        print("API Product with name '{}' does not exist. Creating it in Apigee."
              .format(product_name))
        create_api_product(org_name, product)


if __name__ == '__main__':
    main()
