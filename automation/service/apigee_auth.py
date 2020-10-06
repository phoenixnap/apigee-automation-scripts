#!/usr/local/bin/python
"""Module providing anything related to authenticating with Apigee."""
import requests

def get_access_token(username: str, password: str) -> str:
    """Retrieves an access token from Apigee by using the username and password."""
    result = requests.post(
        'https://login.apigee.com/oauth/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0'},
        data={
            'grant_type': 'password',
            'username': username,
            'password': password})

    if result.status_code != 200:
        raise Exception('Error: {}. \n {}'
                        .format(result.status_code, result.json()))

    print('Successfully retrieved access token from username and password')
    return result.json()['access_token']

def refresh_access_token(refresh_token: str) -> str:
    """Retrieves an access token from Apigee by using the refresh token."""
    result = requests.post(
        'https://login.apigee.com/oauth/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0'},
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token})

    if result.status_code != 200:
        raise Exception('Error: {}. \n {}'
                        .format(result.status_code, result.json()))

    print('Successfully retrieved access token from refresh token')
    return result.json()['access_token']
