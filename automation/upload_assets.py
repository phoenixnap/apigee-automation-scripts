#!/usr/local/bin/python
"""Script which is used to synch all the local assets found in the assets folder with the Apigee portal"""
import argparse
import requests
import os

from service import apigee_auth, apigee_portal, apigee_assets


# Global session used for all requests.
REQUEST = requests.Session()


class LocalFile:
    """Class containing details of an Apigee Portal Asset"""
    def __init__(self,
                 name: str,
                 path: str,
                 size: int):
        self.name = name
        self.path = path
        self.size = size


def get_local_assets(assets_folder: str) -> {}:
    """Retrieves the all current assets from the asset folder."""
    entries = os.scandir(assets_folder)

    local_files = {}

    for entry in entries:
        if entry.is_file():
            local_files[entry.name] = LocalFile(entry.name, entry.path, entry.stat().st_size)

    return local_files


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
        '--folder',
        help='path of the assets folder',
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
    req_grp.add_argument(
        '-c',
        '--clean',
        help='clean any unlisted assets',
        action='store_true')

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error("the following arguments are required: -u/--username "
                     "and -pwd/--password OR -r/--refresh_token")


    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    portal_name = args.portal
    assets_folder = args.folder
    org_name = args.org
    username = args.username
    password = args.password
    refresh_token = args.refresh_token
    clean = args.clean

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

    # Get remote and local assets
    remote_assets = apigee_assets.get_remote_assets(REQUEST, portal.id)
    local_assets = get_local_assets(assets_folder)

    #get differences between sets
    to_add = set(local_assets.keys()) - set(remote_assets.keys())
    to_delete = set(remote_assets.keys()) - set(local_assets.keys())
    to_update = set(remote_assets.keys()).intersection(set(local_assets.keys()))

    for add in to_add:
        apigee_assets.add_remote_asset(REQUEST, portal.id, local_assets[add].path)

    for update in to_update:
        apigee_assets.add_remote_asset(REQUEST, portal.id, local_assets[update].path)

    if clean:
        for path in to_delete:
            apigee_assets.delete_remote_asset(REQUEST, portal.id, org_name, path)


if __name__ == '__main__':
    main()
