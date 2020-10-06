#!/usr/local/bin/python
"""Module providing REST calls related to custom css on Apigee."""
import json

from utils import utils

class Theme:
    """Class containing details of an Apigee Portal theme."""
    def __init__(self, variables: str, overrides: str, custom_scss: str,
                 logo: str, mobile_logo: str, favicon: str):
        self.variables = variables
        self.overrides = overrides
        self.customScss = custom_scss
        self.logo = logo
        self.mobileLogo = mobile_logo
        self.favicon = favicon
        self.editorMode = 'MANAGED_THEME_MODE'
        self.kind = 'theme-editor-update'


def get_current_theme(session, portal_id: str) -> Theme:
    """Retrieves the current theme settings for the current portal."""
    response = session.get(
        'https://apigee.com/portals/api/sites/{}/customcss'.format(portal_id))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully fetched Theme.')

    theme = response.json()['data']
    return Theme(theme['variablesPublished'],
                 theme['overridesPublished'],
                 theme['customScssPublished'],
                 theme['logoUrlPublished'],
                 theme['mobileLogoUrlPublished'],
                 theme['faviconUrlPublished'])


def update_theme(session, portal_id: str, theme: Theme):
    """Updates theme."""
    url = 'https://apigee.com/portals/api/sites/{}/customcss'.format(portal_id)

    response = session.put(url, data=json.dumps(theme.__dict__))

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully uploaded theme to Apigee portal!')


def publish_theme(session, portal_id: str, org_name: str):
    """Publish all changes to the theme theme."""
    url = 'https://apigee.com/portals/api/sites/{}/customcss/publish'.format(portal_id)

    response = session.post(url, json={'orgname': org_name})

    if response.status_code != 200:
        raise Exception(utils.print_error(response))

    print('Successfully published theme to Apigee portal!')
