#!/usr/local/bin/python
"""Some common utilities used by these script"""
import json

def print_error(response) -> str:
    """Prints the error returned from an API call"""

    try:
        body_json = response.json()
        body_str = json.dumps(body_json, indent=2, ensure_ascii=False)
    except Exception:
        text = response.text if hasattr(response, 'text') else ''
        body_str = text[:2000] if text else '<empty body>'

    ct = response.headers.get('Content-Type', '<unknown>')
    req_method = getattr(response.request, 'method', '<unknown>')
    req_url = getattr(response, 'url', '<unknown>')
    reason = getattr(response, 'reason', '')

    return (
        f'Error: {response.status_code} {reason}\n'
        f'Content-Type: {ct}\n'
        f'URL: {req_method} {req_url}\n'
        f'Response body:\n{body_str}'
    )