#!/usr/local/bin/python
"""Module providing REST calls related to the portal on Apigee."""
from utils import utils

import json


class Portal:
    """Class containing details of an Apigee Portal Page."""

    def __init__(self, portal_id: str,
                 name: str,
                 org_name: str,
                 description: str,
                 analytics_script: str,
                 analytics_tracking_id: str,
                 custom_domain: str,
                 current_domain: str,
                 default_domain: str,
                 idp_enabled: bool,
                 portal_version: int,
                 teams: []):
        self.id = portal_id
        self.name = name
        self.orgName = org_name
        self.defaultDomain = default_domain
        self.description = description
        self.analyticsScript = analytics_script
        self.analyticsTrackingId = analytics_tracking_id
        self.customDomain = custom_domain
        self.currentDomain = current_domain
        self.idpEnabled = idp_enabled
        self.portalVersion = portal_version
        self.migrationSrcSiteId = ''
        self.migrationDestSiteId = ''
        self.teams = teams


def get_all_portals(session, org_name: str) -> {}:
    """Retrieves a list of current pages."""
    response = session.get('https://apigee.com/portals/api/sites?orgname={}'.format(org_name))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully fetched all portals.')

    data = response.json()['data']

    all_portals = {}

    for list_item in data:
        all_portals[list_item['name']] = Portal(list_item['id'],
                                                list_item['name'],
                                                list_item['orgName'],
                                                list_item['description'],
                                                list_item['analyticsScript'],
                                                list_item['analyticsTrackingId'],
                                                list_item['customDomain'],
                                                list_item['currentDomain'],
                                                list_item['defaultDomain'],
                                                list_item['idpEnabled'],
                                                list_item['portalVersion'],
                                                list_item['teams'])

    return all_portals


def add_portal(session, org_name: str, portal_name: str, description: str) -> Portal:
    """Adds a portal to the current organization."""
    url = 'https://apigee.com/portals/api/sites'

    data = {'name': portal_name,
            'description': description,
            'id': '',
            'orgName': org_name,
            'analyticsScript': '',
            'analyticsTrackingId': '',
            'customDomain': '',
            'currentDomain': '',
            'lastPublished': 0,
            'idpEnabled': False,
            'portalVersion': 2,
            'migrationSrcSiteId': '',
            'migrationDestSiteId': '',
            'teams': [],
            'zoneId': ''
            }
    response = session.post(url, json=data)

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    response = response.json()['data']

    print('Portal successfully added at: ' + response['defaultDomain'])

    return Portal(response['id'],
                  response['name'],
                  response['orgName'],
                  response['description'],
                  response['analyticsScript'],
                  response['analyticsTrackingId'],
                  response['customDomain'],
                  response['currentDomain'],
                  response['defaultDomain'],
                  response['idpEnabled'],
                  response['portalVersion'],
                  response['teams'])


def update_portal(session, portal: Portal, new_settings: dict):
    """Updates a portal to the current organization."""

    # Update description.
    url = str.format('https://apigee.com/portals/api/sites/{}/portal', portal.id)

    portal.description = new_settings["description"]

    data = json.dumps(portal.__dict__)

    response = session.put(url, data=data)

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    response = response.json()['data']

    print('Portal description successfully added at: ' + response['defaultDomain'])

    # Update analytics.
    analytics = {"analyticsScript": new_settings["analyticsScript"],
                 "analyticsTrackingId": new_settings["analyticsTrackingId"],
                 "orgname": portal.orgName}

    analytics_url = str.format('https://apigee.com/portals/api/sites/{}/site/analytics', portal.id)
    data = json.dumps(analytics)

    response = session.post(analytics_url, data=data)

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Portal analytics successfully updated at: ' + portal.defaultDomain)


def add_or_get_portal(session, org_name: str, portal_name: str, description: str) -> Portal:
    """Method that checks if portal is present in organization, and if not adds it."""

    all_portals = get_all_portals(session, org_name)

    if portal_name in all_portals.keys():
        return all_portals[portal_name]
    else:
        return add_portal(session, org_name, portal_name, description)


def get_portal(session, org_name: str, portal_name: str) -> Portal:
    """Method that checks if portal is present in organization, and if not adds it."""

    all_portals = get_all_portals(session, org_name)

    if portal_name in all_portals.keys():
        return all_portals[portal_name]
    else:
        raise Exception('Portal ' + portal_name + ' does not exist')


def update_domain(session, portal: Portal, new_settings: dict):
    url = str.format('https://apigee.com/portals/api/sites/{}/site/domains', portal.id)

    data = json.dumps(new_settings)
    print(data)

    header = {"Content-Type": "application/json"}

    response = session.post(url, headers=header, data=data)

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    response = response.json()['data']
