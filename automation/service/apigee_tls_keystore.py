"""Module providing REST calls related to the tls keystore on Apigee."""
import datetime
from typing import List
from requests import Response
from requests import Session

APIGEE_API_URL = 'https://api.enterprise.apigee.com/v1/organizations/{}/environments/{}'


class Keystore:
    """Class containing details of an Apigee tls keystore."""

    def __init__(self, name: str):
        self.name = name


class Alias:
    """Class containing details of a keystore alias."""

    def __init__(self, name: str):
        self.name = name


class Cert:
    """Class containing details of a keystore certificate """

    def __init__(self, path_name: str, cert_type: str = "pkcs12"):
        self.cert_type = cert_type
        self.path_name = path_name


def print_error(response: Response) -> str:
    """Prints the error returned from an API call"""
    return f'Error: {response.status_code} - {response.reason}. \n {response.text}'


def get_keystores_list(session: Session, org_name: str, env_name: str) -> List[str]:
    """Retrieves the tls keystores of the given organization name and environment name"""
    response = session.get((APIGEE_API_URL + '/keystores').format(org_name, env_name))

    if response.status_code != 200:
        raise Exception(print_error(response))

    keystores = response.json()
    print(f'Keystore list for Apigee: {keystores}')

    return keystores


def get_cert_list(session: Session, org_name: str, env_name: str, keystore_name: str) -> List[str]:
    """Retrieves the tls keystores of the given organization name and environment name"""
    response = session.get((APIGEE_API_URL + '/keystores/{}/certs').format(org_name, env_name, keystore_name))

    if response.status_code != 200:
        raise Exception(print_error(response))

    certs = response.json()
    print(f'Cert list for keystore: {certs}')

    return certs


def get_aliases_list(session: Session, org_name: str, env_name: str, keystore_name: str) -> List[str]:
    """Retrieves the tls keystores of the given organization name and environment name"""
    response = session.get((APIGEE_API_URL + '/keystores/{}/aliases').format(org_name, env_name, keystore_name))

    if response.status_code != 200:
        raise Exception(print_error(response))

    aliases = response.json()
    print(f'Aliases list for keystore {keystore_name}: {aliases}')

    return aliases


def get_cert_from_alias(session: Session, org_name: str, env_name: str, keystore_name: str) -> str:
    response = session.get(
        (APIGEE_API_URL + '/keystores/{}').format(org_name, env_name, keystore_name))

    if response.status_code != 200:
        raise Exception(print_error(response))
    print(f'Successfully fetched certs details from Apigee keystore: {keystore_name}')
    keystore = response.json()

    cert = keystore['aliases'][0]['cert']
    print('Cert details for keystore: ' + str(cert))

    return cert


def get_cert_detail(session: Session, org_name: str, env_name: str, keystore_name: str, cert_name: str):
    response = session.get(
        (APIGEE_API_URL + '/keystores/{}/certs/{}').format(org_name, env_name, keystore_name, cert_name))

    if response.status_code != 200:
        raise Exception(print_error(response))

    cert = response.json()
    print('Cert details for keystore: ' + str(cert))

    return cert


def check_cert_expiration_date(cert) -> int:
    exp_date = cert['certInfo'][0]['expiryDate']
    exp_date = datetime.datetime.fromtimestamp(exp_date / 1000)
    print(str(exp_date))
    today = datetime.datetime.today()
    print(today)
    period = exp_date - today
    print(period)
    return period.days


def create_keystore(session: Session, org_name: str, env_name: str, keystore_name: str) -> Keystore:
    """Creates a keystore in tls keystores Apigee with the given name"""

    url = (APIGEE_API_URL + '/keystores').format(org_name, env_name)
    data = {
        "name": keystore_name
    }
    headers = {'Content-Type': 'application/json'}
    response = session.post(url, json=data, headers=headers)

    if response.status_code != 201:
        raise Exception(print_error(response))

    json = response.json()
    print(f'Successfully created keystore in Apigee with name: {json}')
    return Keystore(keystore_name)


def create_aliases(session: Session, org_name: str, env_name: str, keystore_name: str, alias_name: str,
                   cert_file: str, key_file: str) -> Alias:
    """Creates an alias in tls keystores Apigee with the given name"""
    url = (APIGEE_API_URL + '/keystores/{}/aliases?alias={}&format={}').format(org_name, env_name, keystore_name,
                                                                               alias_name, "keycertfile")

    files = {
        'certFile': ('fullchain.pem', open(cert_file, 'rb')),
        'keyFile': ('key.pem', open(key_file, 'rb')),
    }

    header = {'Content-Type': 'multipart/form-data'}
    response = session.post(url, headers=header, files=files)

    if response.status_code != 201:
        raise Exception(print_error(response))

    print(f'Successfully created alias in keystore {keystore_name}')
    return Alias(alias_name)


def update_cert(session: Session, org_name: str, env_name: str, keystore_name: str, alias_name: str, path_name: str):
    url = (APIGEE_API_URL + '/keystores/{}/aliases?alias={}&format={}').format(org_name, env_name, keystore_name,
                                                                               alias_name, "pkcs12")

    file_name = {"file": open(path_name, 'rb')}
    header = {'Content-Type': 'multipart/form-data'}

    response = session.put(url, headers=header, files=file_name)

    if response.status_code != 200:
        raise Exception(print_error(response))

    print(f'Successfully created alias in keystore {keystore_name}')
    return Alias(alias_name)


def delete_keystore(session: Session, org_name: str, env_name: str, keystore_name: str):
    url = (APIGEE_API_URL + '/keystores/{}').format(org_name, env_name, keystore_name)

    response = session.delete(url)

    if response.status_code != 200 or response.status_code != 204:
        raise Exception(print_error(response))

    json = response.json()
    print(json)
    print(f'Successfully deleted keystore {keystore_name}')


def update_reference(session: Session, org_name: str, env_name: str, keystore_name: str, ref_name: str):
    url = (APIGEE_API_URL + '/references/' + ref_name).format(org_name, env_name)

    header = {"Content-Type": "application/json"}
    data = {"name": ref_name, "refers": keystore_name, "resourceType": "KeyStore"}
    response = session.put(url, headers=header, json=data)

    if response.status_code != 200:
        raise Exception(print_error(response))

    ref = response.json()
    print(ref)
    return ref


def get_keystore_from_reference(session: Session, org_name: str, env_name: str, ref_name: str) -> str:
    url = (APIGEE_API_URL + '/references/' + ref_name).format(org_name, env_name)

    header = {"Content-Type": "application/json"}
    response = session.get(url, headers=header)

    if response.status_code != 200:
        raise Exception(print_error(response))

    reference = response.json()
    keystore = reference['refers']
    return keystore


def is_cert_expiring(cert: dict, expires_in_days: int) -> bool:
    days = check_cert_expiration_date(cert)
    if days < expires_in_days:
        return True
    return False
