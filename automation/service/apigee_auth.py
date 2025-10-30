#!/usr/local/bin/python
"""Module providing anything related to authenticating with Apigee."""
import re
import requests

def set_headers(session, access_token, org_name, content_type=None):
    """Add Auth Header by default to all requests."""
    if content_type:
        session.headers.update({'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': content_type})
    else:
        session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})
    session.cookies.update({'access_token': access_token})
    session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
    session.headers.update({'X-Apigee-Csrf': get_csrf_token(session)})
    session.headers.update({'X-Apigee-org': org_name})
    session.cookies.update({'access_token': access_token})

def get_csrf_token(session) -> str:
    """Retrieve csrf token from get response"""
    response = session.get('https://apigee.com/edge')
    match = re.search(r'<csrf\s+data="([^"]+)"', response.text)
    if not match:
        print("CSRF token not found")
    return match.group(1)


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
