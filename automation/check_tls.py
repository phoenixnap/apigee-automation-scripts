import argparse
import requests
import sys

from service import apigee_auth, apigee_tls_keystore

# Global session used for all requests.
REQUEST = requests.Session()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='uploads a keystore according to the configured file')
    req_grp = parser.add_argument_group(title='list of arguments')
    req_grp.add_argument(
        '-p',
        '--portal',
        help='name of the portal to update')
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
        '-r',
        '--reference',
        help='name of the tls reference',
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
        '-d',
        '--expires_in_days',
        help='days until certificate expires',
        required=True,
        type=int)
    req_grp.add_argument(
        '-rt',
        '--refresh_token',
        help='apigee OAuth refresh token. If specified, ignores the username and password')

    parsed = parser.parse_args()

    if parsed.refresh_token is None and (parsed.username is None or parsed.password is None):
        parser.error('the following arguments are required: Use either -u/--username and -pwd/--password or '
                     '-rt/--refresh_token')

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()

    org_name = args.org
    env_name = args.env
    ref_name = args.reference
    username = args.username
    password = args.password
    expires_in_days = args.expires_in_days
    refresh_token = args.refresh_token

    if refresh_token is not None:
        access_token = apigee_auth.refresh_access_token(refresh_token)
    else:
        access_token = apigee_auth.get_access_token(username, password)

    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})
    REQUEST.cookies.update({'access_token': access_token})

    keystore_name = apigee_tls_keystore.get_keystore_from_reference(REQUEST, org_name, env_name, ref_name)
    crt = apigee_tls_keystore.get_cert_from_alias(REQUEST, org_name, env_name, keystore_name)

    status = ""
    cert = apigee_tls_keystore.get_cert_detail(REQUEST, org_name, env_name, keystore_name, crt)
    if cert['certName'] == crt:
        status = apigee_tls_keystore.is_cert_expiring(cert, expires_in_days)

    if status != "":
        if status:
            # cert is expiring
            print('Certificate is expiring!')
            sys.exit(2)
        else:
            sys.exit(0)
    else:
        print('Certificate name not found!')
        sys.exit(1)


if __name__ == '__main__':
    main()
