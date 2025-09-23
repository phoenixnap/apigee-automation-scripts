"""Script which is used to upload a tls keystore/certificate to Apigee."""

import argparse
import requests

from service import apigee_auth, apigee_target_servers

# Global session used for all requests.
REQUEST = requests.Session()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='uploads a target server')
    req_grp = parser.add_argument_group(title='list of arguments')
    req_grp.add_argument(
        '-o',
        '--org',
        help='name of the organization',
        required=True)
    req_grp.add_argument(
        '-e',
        '--env',
        help='name of the apigee environment',
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
        help='apigee OAuth refresh token. If specified, ignores the username and password')
    req_grp.add_argument(
        '-n',
        '--name',
        help='name of the target server',
        required=True)
    req_grp.add_argument(
        '-h',
        '--host',
        help='host of the target server',
        required=True)
    req_grp.add_argument(
        '-p',
        '--port',
        help='port of the target server',
        required=True)
    req_grp.add_argument(
        '-e',
        '--isEnabled',
        help='whether the target server is enabled',
        required=True)
    req_grp.add_argument(
        '--ssl-enabled',
        help='whether SSL is enabled',
        required=True)
    req_grp.add_argument(
        '--ssl-ciphers',
        help='list of SSL ciphers (comma separated)',
        required=False)
    req_grp.add_argument(
        '--ssl-protocols',
        help='list of SSL protocols (comma separated)',
        required=False)
    req_grp.add_argument(
        '--ssl-client-auth',
        help='whether client authentication is enabled',
        required=False)
    req_grp.add_argument(
        '--ssl-ignore-validation',
        help='ignore SSL validation errors (true/false)',
        required=False)
    req_grp.add_argument(
        '--ssl-truststore',
        help='truststore name or path',
        required=False)
    req_grp.add_argument(
        '--ssl-key-alias',
        help='SSL key alias',
        required=False)
    req_grp.add_argument(
        '--ssl-keystore',
        help='SSL keystore name',
        required=False)

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error('the following arguments are required: Use either -u/--username and -pwd/--password or -rt/--refresh_token')

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    org_name = args.org
    env_name = args.env
    username = args.username
    password = args.password
    refresh_token = args.refresh_token

    target_name = args.name
    target_host = args.host
    target_port = args.port
    target_is_enabled = args.isEnabled

    ssl_enabled = args.ssl_enabled
    ssl_ciphers = args.ssl_ciphers
    ssl_protocols = args.ssl_protocols
    ssl_client_auth = args.ssl_client_auth
    ssl_ignore_validation = args.ssl_ignore_validation
    ssl_truststore = args.ssl_truststore
    ssl_key_alias = args.ssl_key_alias
    ssl_keystore = args.ssl_keystore


    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})
    REQUEST.cookies.update({'access_token': access_token})

    # Override if portal name was passed as a switch.
    if portal_name:
        config['name'] = portal_name

    # Get target server
    target_server = apigee_target_servers.get_target_server(REQUEST, org_name, env_name, target_name)


    if target_server:
        print("Target server {} already exists. Updating it...".format(target_name))
        apigee_target_servers.update_target_server(REQUEST, org_name, env_name, target_name,
                                                  target_host, target_port, target_is_enabled,
                                                  ssl_enabled, ssl_ciphers, ssl_protocols,
                                                  ssl_client_auth, ssl_ignore_validation,
                                                  ssl_truststore, ssl_key_alias, ssl_keystore)
    else:
        print("Target server {} does not exist. Creating it...".format(target_name))
        apigee_target_servers.create_target_server(REQUEST, org_name, env_name, target_name,
                                                  target_host, target_port, target_is_enabled,
                                                  ssl_enabled, ssl_ciphers, ssl_protocols,
                                                  ssl_client_auth, ssl_ignore_validation,
                                                  ssl_truststore, ssl_key_alias, ssl_keystore)

    

if __name__ == '__main__':
    main()
