#!/usr/local/bin/python
"""REST calls to add or delete assets from an apigee portal."""
from utils import utils


class Asset:
    """Class containing details of an Apigee Portal Asset."""
    def __init__(self,
                 file_name: str,
                 full_url: str,
                 extension: str,
                 rel_url: str,
                 thumb_url: str,
                 width: str,
                 height: str,
                 size: str,
                 modified: str,
                 image: str,
                 versioned_rel_url: str):
        self.filename = file_name
        self.fullUrl = full_url
        self.extension = extension
        self.relUrl = rel_url
        self.thumbUrl = thumb_url
        self.width = width
        self.height = height
        self.size = size
        self.modified = modified
        self.image = image
        self.versionedRelUrl = versioned_rel_url


def get_remote_assets(session, portal_id: str) -> {}:
    """Retrieves a list of current assets."""

    response = session.get(
        'https://apigee.com/portals/api/sites/{}/file/list'.format(portal_id))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully fetched all assets.')

    fetched_assets = response.json()['data']

    assets = {}

    for list_item in fetched_assets:
        assets[list_item['filename']] = Asset(list_item['filename'],
                                              list_item['fullUrl'],
                                              list_item['extension'],
                                              list_item['relUrl'],
                                              list_item['thumbUrl'],
                                              list_item['width'],
                                              list_item['height'],
                                              list_item['size'],
                                              list_item['modified'],
                                              list_item['image'],
                                              list_item['versionedRelUrl'])

    return assets


def delete_remote_asset(session, portal_id: str, org_name: str, file_name: str):
    """Delete an asset from the remote site."""
    url = 'https://apigee.com/portals/api/sites/{}/file/delete'.format(portal_id)

    response = session.post(url, json={'orgname': org_name, 'filename': file_name})

    if response.status_code != 200:
        print(utils.print_error(response))
    else:
        print('Successfully deleted ' + file_name + ' from Apigee portal!')


def add_remote_asset(session, portal_id: str, local_file_path: str):
    """Upload an asset to the portal."""
    url = 'https://apigee.com/portals/api/sites/{}/file/post'.format(portal_id)

    # Make sure the the dictionary's key is 'file'.
    file = open(local_file_path, 'rb')
    response = session.post(url, files={'file': file})

    if response.status_code != 200:
        raise Exception(
            utils.print_error(response))

    print('Successfully uploaded ' + local_file_path + ' to Apigee portal!')
