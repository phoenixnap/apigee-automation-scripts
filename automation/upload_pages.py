#!/usr/local/bin/python
"""Script which is used to update the portal them on an Apigee portal"""
import argparse
import os
import requests
import json

from service import apigee_auth, apigee_portal, apigee_menuitems, apigee_pages

# Global session used for all requests.
REQUEST = requests.Session()


def get_local_pages(pages_folder: str) -> {}:
    """Retrieves the all html pages from the folder."""
    entries = os.scandir(pages_folder)

    local_pages = {}

    for entry in entries:
        if entry.is_file() \
                and (entry.name.endswith('.html')
                     or entry.name.endswith('.htm')
                     or entry.name.endswith('.md')):
            file_name = os.path.splitext(entry.name)[0]
            local_pages[file_name] = open(entry.path, 'r', encoding='utf8').read()

    return local_pages


def add_menu_items(portal_name: str, org_name: str, pages: {},
                   items: [], menu_item_type: apigee_menuitems.MenuItemType):
    """Add all menu items, retrieved from the structure"""
    priority = 1

    for menu_item in items:
        page_id = None
        url = '#'

        if menu_item['url'] is not None:
            url = menu_item['url']

        if menu_item['page'] is not None:
            url = menu_item['page']
            if url in pages:
                page_id = pages[url].id

        apigee_menuitems.add_menu_item(REQUEST, portal_name, org_name, menu_item['name'],
                                       url, page_id, priority, False, menu_item_type)
        priority = priority + 1

        #Create sub menus
        for sub_menu in menu_item['sub_menu']:
            sub_menu_page_id = None
            sub_menu_url = '#'

            if sub_menu['url'] is not None:
                sub_menu_url = sub_menu['url']

            if sub_menu['page'] is not None:
                sub_menu_url = sub_menu['page']
                if sub_menu_url in pages:
                    sub_menu_page_id = pages[sub_menu_url].id

            apigee_menuitems.add_menu_item(REQUEST, portal_name, org_name, sub_menu['name'],
                                           sub_menu_url, sub_menu_page_id, priority, True, menu_item_type)
            priority = priority + 1

    apigee_menuitems.publish_menu_items(REQUEST, org_name, portal_name)


def refresh_menu_items(session, portal_name, org_name: str, menu_items_config: str):
    """Refresh all menu items according to config file."""
    apigee_menuitems.delete_all_menu_items(session, portal_name)
    pages = apigee_pages.get_remote_pages(session, portal_name)
    menu_item_types = apigee_menuitems.get_all_menu_item_types(session, portal_name)

    data = open(menu_items_config, 'r', encoding='utf8').read()
    header = json.loads(data)['header']
    footer = json.loads(data)['footer']

    add_menu_items(portal_name, org_name, pages, header, menu_item_types['primary'])
    add_menu_items(portal_name, org_name, pages, footer, menu_item_types['footer'])


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
        help='path of the pages folder',
        required=True)
    req_grp.add_argument(
        '-m',
        '--menu',
        help='path to menu items configuration',
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

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error("the following arguments are required: -u/--username and -pwd/--password OR -r/--refresh_token")

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    portal_name = args.portal
    pages_folder = args.folder
    org_name = args.org
    username = args.username
    password = args.password
    refresh_token = args.refresh_token
    menu_items_config = args.menu

    # Retrieve an access token using the refresh token provided. This ensures
    # that we always have a valid access token.
    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'})

    # Check portal and add it if not present
    portal = apigee_portal.get_portal(REQUEST, org_name, portal_name)

    # Get remote and local pages
    remote_pages = apigee_pages.get_remote_pages(REQUEST, portal.id)
    local_pages = get_local_pages(pages_folder)

    # Get differences between local and remote pages
    to_add = set(local_pages.keys()) - set(remote_pages.keys())
    to_delete = set(remote_pages.keys()) - set(local_pages.keys())
    to_update = set(remote_pages.keys()).intersection(set(local_pages.keys()))

    for friendly_id in to_delete:
        apigee_pages.delete_remote_page(REQUEST, portal.id, remote_pages[friendly_id].id)

    for add in to_add:
        apigee_pages.add_update_remote_page(REQUEST, portal.id, org_name, None, add, local_pages[add])

    for update in to_update:
        apigee_pages.add_update_remote_page(REQUEST, portal.id, org_name, remote_pages[update].id, update, local_pages[update])

    # Refresh menu items
    refresh_menu_items(REQUEST, portal.id, org_name, menu_items_config)


if __name__ == '__main__':
    main()
