#!/usr/local/bin/python
"""Script to generate an Apigee analytics report."""

import json
import argparse
import time
import requests

from service import apigee_auth, apigee_reports

# Global session used for all requests.
REQUEST = requests.Session()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='generate an Apigee analytics report')
    arg_grp = parser.add_argument_group(title='accepted arguments')
    arg_grp.add_argument(
        '-f',
        '--file',
        help='path of the analytics query JSON file',
        required=True)
    arg_grp.add_argument(
        '-o',
        '--org',
        help='name of the organization',
        required=True)
    arg_grp.add_argument(
        '-e',
        '--env',
        help='existing environment in the organization to base the report on',
        required=True)
    arg_grp.add_argument(
        '-out',
        '--output',
        help='file location of the query output',
        required=False)
    arg_grp.add_argument(
        '-sd',
        '--startdate',
        help='ISO 8601 (yyyy-MM-ddTHH:mm:ss) UTC date format indicating report start date',
        required=True)
    arg_grp.add_argument(
        '-ed',
        '--enddate',
        help='ISO 8601 (yyyy-MM-ddTHH:mm:ss) UTC date format indicating report end date',
        required=True)
    arg_grp.add_argument(
        '-gtu',
        '--groupbytimeunit',
        help="Time unit used to group the result set. Valid values include: second, minute, hour, day, week, or month",
        required=False
    )
    arg_grp.add_argument(
        '-u',
        '--username',
        help='apigee user')
    arg_grp.add_argument(
        '-pwd',
        '--password',
        help='apigee password')
    arg_grp.add_argument(
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

    query_path = args.file
    org_name = args.org
    env = args.env
    output_path = args.output
    start_date = args.startdate
    end_date = args.enddate
    group_by_time_unit = args.groupbytimeunit
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
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    # Read JSON file containing analytics query setup information.
    data = open(query_path, 'r').read()
    query = json.loads(data)

    # Set the start and end date for the report in the given JSON.
    # This is so that the dates can be modified flexibly without modifying the JSON.
    query.update({'timeRange': {'start': start_date, 'end': end_date}})

    # Set the groupByTimeUnit if provided in the query
    if group_by_time_unit is not None:
        query.update({'groupByTimeUnit': group_by_time_unit})

    query = apigee_reports.generate_async_query(REQUEST, org_name, env, query)

    print('Please wait while report finishes compiling.')
    while query.state != 'completed':
        # Wait 5 seconds before checking if the query has completed.
        time.sleep(5)
        query = apigee_reports.get_query_status(REQUEST, query.url)

    # If the output path is specified, save the result there.
    if not output_path:
        apigee_reports.get_query_result(REQUEST, query.url)
    else:
        apigee_reports.get_query_result(REQUEST, query.url, output_path)


if __name__ == '__main__':
    main()
    