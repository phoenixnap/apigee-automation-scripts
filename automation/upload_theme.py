#!/usr/local/bin/python
"""Script which is used to update the portal them on an Apigee portal."""
import argparse
import json
import base64
import requests

from service import apigee_auth, apigee_customcss, apigee_portal


# Global session used for all requests.
REQUEST = requests.Session()


def load_local_theme(theme_config_filename: str) -> apigee_customcss.Theme:
    """Retrieves the current theme settings for the current portal."""
    data = open(theme_config_filename, 'r', encoding='utf8').read()
    config = json.loads(data)

    variable_overrides = ''
    custom_css = ''
    logo = ''
    mobile_logo = ''
    favicon = ''

    if config['overridesFile']:
        variable_overrides = open(config['overridesFile'], 'r', encoding='utf8').read()

    if config['customScssFile']:
        custom_css = open(config['customScssFile'], 'r', encoding='utf8').read()

    if config['logoFile']:
        with open(config['logoFile'], "rb") as image_file:
            logo = base64.b64encode(image_file.read()).decode('utf-8')

    if config['mobileLogoFile']:
        with open(config['mobileLogoFile'], "rb") as image_file:
            mobile_logo = base64.b64encode(image_file.read()).decode('utf-8')

    if config['faviconFile']:
        with open(config['faviconFile'], "rb") as image_file:
            favicon = base64.b64encode(image_file.read()).decode('utf-8')

    default_variables = '{\"variables\":{\"primary\":{\"kind\":\"color-mat\",\"value\":\"$mat-grey\",\"defaultHue\":\"800\",\"lighterHue\":\"100\",\"darkerHue\":\"900\"},\"accent\":{\"kind\":\"color-mat\",\"value\":\"$mat-grey\",\"defaultHue\":\"500\",\"lighterHue\":\"100\",\"darkerHue\":\"700\"}}}'
    return apigee_customcss.Theme(default_variables,
                                  variable_overrides,
                                  custom_css,
                                  logo,
                                  mobile_logo,
                                  favicon)


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
        '--file',
        help='path of the theme configuration file',
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
    configuration_path = args.file
    org_name = args.org
    username = args.username
    password = args.password
    refresh_token = args.refresh_token

    # Retrieve an access token using the refresh token provided. This ensures
    # that we always have a valid access token.
    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'})
    REQUEST.cookies.update({'access_token': access_token})

    # Check portal and add it if not present
    portal = apigee_portal.get_portal(REQUEST, org_name, portal_name)

    new_theme = load_local_theme(configuration_path)

    if new_theme is not None:
        apigee_customcss.update_theme(REQUEST, portal.id, new_theme)
        apigee_customcss.publish_theme(REQUEST, portal.id, org_name)


if __name__ == '__main__':
    main()
