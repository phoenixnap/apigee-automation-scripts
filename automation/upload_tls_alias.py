"""Script which is used to upload a tls keystore/certificate to Apigee."""

import argparse
import requests

from service import apigee_auth, apigee_tls_keystore

# Global session used for all requests.
REQUEST = requests.Session()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='uploads a keystore according to the configured file')
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
        '-k',
        '--keystore',
        help='name of the keystore',
        required=True)
    req_grp.add_argument(
        '-a',
        '--alias',
        help='name of the alias',
        required=True)
    req_grp.add_argument(
        '-cf',
        '--cert_file',
        help='local file path of the pem certificate file',
        required=True)
    req_grp.add_argument(
        '-kf',
        '--key_file',
        help='local file path of the pem private key file',
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

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error('the following arguments are required: Use either -u/--username and -pwd/--password or -rt/--refresh_token')

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    org_name = args.org
    env_name = args.env
    keystore_name = args.keystore
    alias_name = args.alias
    cert_file = args.cert_file
    key_file = args.key_file
    username = args.username
    password = args.password
    refresh_token = args.refresh_token

    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': f'Bearer {access_token}'})

    # Retrieve all the keystore
    keystores_list = apigee_tls_keystore.get_keystores_list(REQUEST, org_name, env_name)

    # Create keystore if not exist
    if keystore_name not in keystores_list:
        print('Keystore does not exist - creating it on Apigee')
        apigee_tls_keystore.create_keystore(REQUEST, org_name, env_name, keystore_name)

    # Retrieve all the aliases of keystore
    alias_list = apigee_tls_keystore.get_aliases_list(REQUEST, org_name, env_name, keystore_name)

    # Create a new alias for the keystore on Apigee if there isn't an existing one.
    if alias_name not in alias_list:
        print('Alias does not exist - creating it on Apigee.')
        alias = apigee_tls_keystore.create_aliases(REQUEST, org_name, env_name, keystore_name,
                                                   alias_name, cert_file, key_file)
        print(f'Alias is successfully created and certificate uploaded! {alias}')
    else:
        print('Certificate updated!')
        apigee_tls_keystore.update_cert(REQUEST, org_name, env_name, keystore_name, alias_name, cert_file)


if __name__ == '__main__':
    main()
