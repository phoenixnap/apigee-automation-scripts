#!/usr/local/bin/python
from utils import utils
"""Script containing REST calls to generate an Apigee query, get its status and download the result."""

import zipfile
import io
import os


class Query:
    """Class containing details related to an Apigee query."""
    def __init__(self, url: str, state: str, created: str):
        super().__init__()
        self.url = url
        self.state = state
        self.created = created


def get_query_status(session, query_url: str) -> Query:
    """Get the current status of an Apigee async query."""

    response = session.get('https://api.enterprise.apigee.com/v1{}'.format(query_url))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    data = response.json()
    query = Query(data['self'], data['state'], data['created'])
    print('Query status: {}.'.format(query.state))

    return query


def generate_async_query(session, org_name: str, env: str, data: str) -> Query:
    """Instructs Apigee to start processing an async query with the data provided."""

    response = session.post('https://api.enterprise.apigee.com/v1/organizations/{}/environments/{}/queries'.format(org_name, env), json=data)

    if response.status_code != 201:
        raise Exception(utils.print_error(response))

    data = response.json()
    query = Query(data['self'], data['state'], data['created'])

    print('Successfully created an async query. Query status: {}.'.format(query.state))

    return query


def get_query_result(session, query_url: str, output_path=os.getcwd()) -> str:
    """Get the Apigee async query result in zip format. This is then extracted
    and the output is saved as '.csv.gz' either in the current directory or 
    in the one provided."""

    response = session.get('https://api.enterprise.apigee.com/v1{}/result'.format(query_url))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully fetched query result.')

    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(output_path)

    location = output_path + '/' + z.filelist[0].filename
    print('File stored in: {}'.format(location))

    return location
