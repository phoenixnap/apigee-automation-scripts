#!/usr/local/bin/python
"""Script which is used to link an API Product to an API spec and expose it on an Apigee Portal."""
import argparse
import json
import requests
import time

from service import apigee_auth, apigee_portal
from utils import utils
from exceptions.rest_exception import RestException


# Global session used for all requests.
REQUEST = requests.Session()


class ApiDoc():
    """Represents an API Portal Documentation."""

    def __init__(self, doc_id: int, spec_name: str, spec_id: str):
        self.doc_id = doc_id
        self.spec_name = spec_name
        self.spec_id = spec_id


def spec_exists(org_name: str, spec_name: str) -> bool:
    """Checks whether a given spec exists inside a given Apigee organization.
       Returns the spec ID if it exists."""
    response = REQUEST.get(
        'https://apigee.com/dapi/api/organizations/{}/specs/folder/home'.format(org_name))

    if response.status_code != 200:
        raise RestException(utils.print_error(response))

    print('Successfully fetched OpenAPI Specs from Apigee.')

    for spec in response.json()['contents']:
        if spec['name'] == spec_name:
            return spec['id']

    return None


def documentation_exists(
        spec_name: str,
        portal_name: str,
        page_size: int) -> ApiDoc:
    """Retrieves a list of API Products exposed on a portal and checks if
       there is an existing one using the given spec name."""

    response = REQUEST.get(
        'https://apigee.com/portals/api/sites/{}/apidocs?pageSize={}'.format(portal_name, page_size))

    if response.status_code != 200:
        raise RestException(utils.print_error(response))

    for doc in response.json()['data']:
        # Spec ID returned by the API is actually the spec name.
        if doc['specId'] == spec_name:
            return ApiDoc(doc['id'], doc['specId'], doc['specContent'])

    return None


def update_api_documentation(
        api_doc: ApiDoc,
        doc: dict,
        portal_name: str):
    """Updates an existing Portal API Documentation to be in sync with the latest API spec and
       also includes any changes done in the JSON file."""
    print("Updating API documentation on portal '{}' for spec '{}' with doc_id {}".format(
        portal_name,
        api_doc.spec_name,
        api_doc.doc_id))

    response = REQUEST.put(
        'https://apigee.com/portals/api/sites/{}/apidocs/{}/snapshot'.format(
            portal_name, api_doc.doc_id))

    print("snapshot response code: {} and content : {}".format(
        response.status_code,
        response.content))

    if response.status_code != 200:
        raise RestException(utils.print_error(response))

    response = REQUEST.put(
        'https://apigee.com/portals/api/sites/{}/apidocs/{}'.format(
            portal_name, api_doc.doc_id), json=doc)

    if response.status_code != 200:
        raise RestException(utils.print_error(response))

    print(
        "Successfully updated API documentation on portal '{}' for spec '{}'".format(
            portal_name,
            api_doc.spec_name))


def create_api_documentation(doc: dict, portal_name: str):
    """Creates documentation in the given Apigee API Portal
       with the specified details in the JSON file."""

    spec_id = doc['specId']

    print("Creating API documentation on portal '{}' for spec '{}'".format(
        portal_name,
        spec_id))

    response = REQUEST.post(
        'https://apigee.com/portals/api/sites/{}/apidocs'.format(portal_name),
        json=doc)

    if response.status_code != 200:
        raise RestException(utils.print_error(response))

    print(
        "Successfully created API documentation on portal '{}' for spec '{}'".format(
            portal_name,
            spec_id))


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='links an API Product to an API spec and expose it on an Apigee Portal')
    req_grp = parser.add_argument_group(title='required arguments')
    req_grp.add_argument(
        '-f',
        '--file',
        help='path of the Portal documentation JSON file',
        required=True)
    req_grp.add_argument(
        '-s',
        '--spec_name',
        help='name of the OpenAPI Spec',
        required=True)
    req_grp.add_argument(
        '-p',
        '--portal',
        help='name of the portal',
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
    req_grp.add_argument(
        '-pgs',
        '--page_size',
        help='page size for API calls that use paging - default is 100')

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error("the following arguments are required: -u/--username and -pwd/--password OR -r/--refresh_token")

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    doc_path = args.file
    spec_name = args.spec_name
    portal = args.portal
    org_name = args.org
    username = args.username
    password = args.password
    refresh_token = args.refresh_token

    # Some API calls make use of paging, if the page size is not defined, we default it to 100.
    page_size = 100 if args.page_size is None else args.page_size

    data = open(doc_path, 'r', encoding='utf8').read()
    doc = json.loads(data)

    # Organization name might change according to the environment. so update the json
    # with the organization name given as an argument. Spec name also needs to be provided
    # as an argument for ease of use when using this script along with upload_spec.py.
    doc.update({'orgname': org_name, 'specId': spec_name})

    # Retrieve an access token using the refresh token provided. This ensures
    # that we always have a valid access token.
    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    #Check portal and add it if not present
    current_portal = apigee_portal.get_portal(REQUEST, org_name, portal)

    # We do not want to create portal documentation if the spec given does not
    # exist on Apigee.
    spec_id = spec_exists(org_name, spec_name)
    if not spec_id:
        raise RestException(
            "Spec with name '{}' does not exist in Apigee.".format(spec_name))

    # Spec IDs might change all the time, and we use the name as our ID.
    # Therefore, use the spec name specified in the JSON file and fetch
    # the spec ID dynamically.
    doc.update({'specContent': spec_id})

    api_doc = documentation_exists(spec_name, current_portal.id, page_size)
    if api_doc:
        print("API Doc already exists.")
        try:
            update_api_documentation(api_doc, doc, current_portal.id)
        except RestException:
            # Retry since this call fails intermittently
            print("First put call failed ... retrying")
            time.sleep(5)
            update_api_documentation(api_doc, doc, current_portal.id)
    else:
        print("API Doc does not currently exist.")
        create_api_documentation(doc, current_portal.id)


if __name__ == '__main__':
    main()
