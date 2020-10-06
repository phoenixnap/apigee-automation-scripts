#!/usr/local/bin/python
"""Some common utilities used by these script"""


def print_error(response) -> str:
    """Prints the error returned from an API call"""
    return 'Error: {}. \n {}'.format(response.status_code, response.json())
