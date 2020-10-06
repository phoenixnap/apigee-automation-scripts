#!/usr/local/bin/python
"""Module providing REST calls related to pages on Apigee."""
import re

from utils import utils


class Page:
    """Class containing details of an Apigee Portal Page."""
    def __init__(self, content: str, description: str, friendly_id: str, page_id: int, name: str):
        self.content = content
        self.description = description
        self.friendlyId = friendly_id
        self.id = page_id
        self.name = name


def get_remote_pages(session, portal_id: str) -> {}:
    """Retrieves a list of current pages."""

    response = session.get(
        'https://apigee.com/portals/api/sites/{}/pages'.format(portal_id))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully fetched all pages.')

    all_pages = response.json()['data']

    pages = {}

    for list_item in all_pages:
        pages[list_item['friendlyId']] = Page(list_item['content'],
                                              list_item['description'],
                                              list_item['friendlyId'],
                                              list_item['id'],
                                              list_item['name'])

    return pages


def add_update_remote_page(session, portal_id: str, org_name: str, page_id: int,
                           friendly_id: str, content: str):
    """Upload an html page to the portal."""
    if page_id is None:
        url = 'https://apigee.com/portals/api/sites/{}/pages'.format(portal_id)

        data = {'showActionButtons': 'false',
                'type': 'GENERIC',
                'generatedContent': [],
                'name': re.sub('([-]+)', r' ', friendly_id).lower().title(),
                'friendlyId': friendly_id,
                'description': '',
                'orgname': org_name}
        response = session.post(url, json=data)

        if response.status_code != 200:
            raise Exception(utils.print_error(response))

        page_id = response.json()['data']['id']
        print('Successfully added ' + friendly_id + ' page to Apigee portal!')

    #Update the content of the page
    content_url = 'https://apigee.com/portals/api/sites/{}/pages/{}/content'.format(portal_id, str(page_id))
    put_response = session.put(content_url, json={'orgname': org_name, 'content': content})

    if put_response.status_code != 200:
        raise Exception(utils.print_error(put_response))

    publish_url = 'https://apigee.com/portals/api/sites/{}/pages/{}/publish'.format(portal_id, str(page_id))
    publish_response = session.post(publish_url, json={'orgname': org_name})

    if publish_response.status_code != 200:
        raise Exception(utils.print_error(publish_response))

    print('Successfully published ' + friendly_id + ' page to Apigee portal!')


def delete_remote_page(session, portal_id: str, page_id: int):
    """Delete a page from the remote site."""
    url = 'https://apigee.com/portals/api/sites/{}/pages/{}'.format(portal_id, page_id)

    response = session.delete(url)

    if response.status_code != 200:
        print(utils.print_error(response))
    else:
        print('Successfully deleted ' + str(page_id) + ' from Apigee portal!')