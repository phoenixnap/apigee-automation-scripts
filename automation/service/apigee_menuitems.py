#!/usr/local/bin/python
"""Module providing REST calls related to menu items on Apigee."""
from utils import utils


class MenuItemType:
    """Class containing details of an Apigee Menu Type."""
    def __init__(self,
                 friendly_id: str,
                 menu_type_id: str,
                 name: str):
        self.friendlyId = friendly_id
        self.menuTypeId = menu_type_id
        self.name = name


def get_all_menu_item_types(session, portal_id: str) -> {}:
    """Retrieves a list of all menu items types.  These are usually primary and footer."""

    response = session.get(
        'https://apigee.com/portals/api/sites/{}/menutypes'.format(portal_id))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully fetched all menu items.')

    all_menu_types = response.json()['data']

    menu_items = {}

    for list_item in all_menu_types:
        menu_items[list_item['friendlyId']] = MenuItemType(list_item['friendlyId'],
                                                           list_item['menuTypeId'],
                                                           list_item['name'])

    return menu_items


def add_menu_item(session, portal_id: str, org_name: str, name: str, menu_url: str, page_id: int,
                  priority: int, indented: bool, menu_item_type: MenuItemType):
    """Add a menu item to the portal."""
    url = 'https://apigee.com/portals/api/sites/{}/menuitems'.format(portal_id)

    menu_type_id = menu_item_type.menuTypeId
    css_class = menu_item_type.name

    data = {'cssClass': css_class,
            'menuTypeId': menu_type_id,
            'name': name,
            'orgname': org_name,
            'pageId': page_id,
            'priority': priority,
            'url': menu_url,
            'isNested': indented}
    response = session.post(url, json=data)

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    menu_item_id = response.json()['data']['menuItemId']
    print('Successfully added menu_item:' + name + ' page to Apigee portal!')


def publish_menu_items(session, org_name: str, portal_id: str):
    """Rest call to pulish any changes done to menu items."""
    publish_url = 'https://apigee.com/portals/api/sites/{}/menuitems/publish'.format(portal_id)
    publish_response = session.post(publish_url, json={'orgname': org_name})

    if publish_response.status_code != 200:
        raise Exception(utils.print_error(publish_response))

    print('Successfully published all menu items to Apigee portal!')


def delete_all_menu_items(session, portal_id: str):
    """Retrieves a list of current menu items."""
    response = session.get(
        'https://apigee.com/portals/api/sites/{}/menuitems'.format(portal_id))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully fetched all menu items.')

    menu_items = response.json()['data']

    # Delete all menu items from the remote site.
    for menu_item in menu_items:
        url = 'https://apigee.com/portals/api/sites/{}/menuitems/{}'.format(portal_id, str(menu_item['menuItemId']))

        response = session.delete(url)

        if response.status_code != 200:
            print(utils.print_error(response))
        else:
            print('Successfully deleted menu_item:' + str(menu_item['menuItemId']) + ' from Apigee portal!')
