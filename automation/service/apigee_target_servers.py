"""Module providing REST calls related to the target server on Apigee."""
import datetime
from typing import List
from requests import Response
from requests import Session

APIGEE_API_URL = 'https://api.enterprise.apigee.com/v1/organizations/{}/environments/{}'


def print_error(response: Response) -> str:
    """Prints the error returned from an API call"""
    return f'Error: {response.status_code} - {response.reason}. \n {response.text}'


def get_target_server(session: Session, org_name: str, env_name: str, target_server_name: str):
    """Retrieves the target server by name of the given organization name and environment name"""

    response = session.get((APIGEE_API_URL + '/targetservers/{}').format(org_name, env_name, target_server_name))

    if response.status_code == 404:
        return None

    if response.status_code == 200:
        return response.json()

    raise Exception(print_error(response))

