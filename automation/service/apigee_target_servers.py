"""Module providing REST calls related to the target server on Apigee."""
import datetime
import json
from typing import List
from requests import Response
from requests import Session

APIGEE_API_URL = 'https://api.enterprise.apigee.com/v1/organizations/{}/environments/{}'

class SslInfo:
    """Class containing details of the SSL configuration."""
    def __init__(self, enabled: str, ciphers: list, protocols: list,
                 clientAuthEnabled: str, ignoreValidationErrors: bool,
                 trustStore: str, keyAlias: str, keyStore: str):
        self.enabled = enabled
        self.ciphers = ciphers
        self.protocols = protocols
        self.clientAuthEnabled = clientAuthEnabled
        self.ignoreValidationErrors = ignoreValidationErrors
        self.trustStore = trustStore
        self.keyAlias = keyAlias
        self.keyStore = keyStore


class TargetServer:
    """Class containing details of the target server configuration."""
    def __init__(self, name: str, host: str, port: int, isEnabled: bool, sSLInfo: dict):
        self.name = name
        self.host = host
        self.port = port
        self.isEnabled = isEnabled
        # Convertimos el dict en un objeto SslInfo
        self.sSLInfo = SslInfo(**sSLInfo)

def print_error(response: Response) -> str:
    """Prints the error returned from an API call"""
    return f'Error: {response.status_code} - {response.reason}. \n {response.text}'


def get_target_server(session: Session, org_name: str, env_name: str, target_server_name: str):
    """Retrieves the target server by name of the given organization name and environment name"""

    response = session.get((APIGEE_API_URL + '/targetservers/{}').format(org_name, env_name, target_server_name))

    if response.status_code == 404:
        return None

    if response.status_code == 200:
        return response.json()

    raise Exception(print_error(response))

def create_target_server(session: Session, org_name: str, env_name: str, targetServer: TargetServer) -> TargetServer:
    """Creates a target server with the given configuration object"""
    url = (APIGEE_API_URL + '/targetservers').format(org_name, env_name)

    payload = {
        "name": targetServer.name,
        "host": targetServer.host,
        "port": targetServer.port,
        "isEnabled": targetServer.isEnabled,
        "sSLInfo": {
            "enabled": targetServer.sSLInfo.enabled,
            "ciphers": targetServer.sSLInfo.ciphers,
            "protocols": targetServer.sSLInfo.protocols,
            "clientAuthEnabled": targetServer.sSLInfo.clientAuthEnabled,
            "ignoreValidationErrors": targetServer.sSLInfo.ignoreValidationErrors,
            "trustStore": targetServer.sSLInfo.trustStore,
            "keyAlias": targetServer.sSLInfo.keyAlias,
            "keyStore": targetServer.sSLInfo.keyStore
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = session.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code != 201:
        raise Exception(print_error(response))

    print(f'Successfully created target server {targetServer.name}')
    return targetServer

def update_target_server(session: Session, org_name: str, env_name: str, targetServer: TargetServer) -> TargetServer:
    """Updates a target server with the given configuration object"""
    url = (APIGEE_API_URL + '/targetservers').format(org_name, env_name)

    payload = {
        "name": targetServer.name,
        "host": targetServer.host,
        "port": targetServer.port,
        "isEnabled": targetServer.isEnabled,
        "sSLInfo": {
            "enabled": targetServer.sSLInfo.enabled,
            "ciphers": targetServer.sSLInfo.ciphers,
            "protocols": targetServer.sSLInfo.protocols,
            "clientAuthEnabled": targetServer.sSLInfo.clientAuthEnabled,
            "ignoreValidationErrors": targetServer.sSLInfo.ignoreValidationErrors,
            "trustStore": targetServer.sSLInfo.trustStore,
            "keyAlias": targetServer.sSLInfo.keyAlias,
            "keyStore": targetServer.sSLInfo.keyStore
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = (session.put(url, headers=headers, data=json.dumps(payload)))

    if response.status_code != 201:
        raise Exception(print_error(response))

    print(f'Successfully updated target server {targetServer.name}')
    return targetServer
