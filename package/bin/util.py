import sys
import os
import json
import time
import datetime
import time
import requests
import traceback
import logging
import logging.handlers
import urllib3
from typing import Union


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""util.py: This module contains utility functions for the package. These functions are used by the package's scripts.
    
    Functions:
        get_dynatrace_tenant: Get the Dynatrace tenant from the input.
        get_dynatrace_api_token: Get the Dynatrace API token from the input.
        get_dynatrace_collection_interval: Get the Dynatrace collection interval from the input.
        get_dynatrace_entity_cursor: Get the Dynatrace entity cursor from the input.
        get_dynatrace_entity_end"""

__author__ = "David Connett"
__version__ = "1.0.0"
__maintainer__ = "David Connett"
__email__ = "dconnett@splunk.com"
__status__ = "Development"
__license__ = "Splunk General Terms"

script_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.dirname(script_dir)

dynatrace_managed_uri_v2 = 'https://{your-domain}/e/{your-environment-id}/api/v2'
dynatrace_saas_uri_v2 = 'https://{your-enviroment-id}.live.dynatrace.com/api/v2'
dynatrace_environment_active_gate_v2 = 'https://{your-domain}/e/{your-environment-id}/api/v2'

v2_endpoints = {'metrics': '/api/v2/metrics',
                'metrics_query': '/api/v2/metrics/query',
                'metrics_descriptors': '/api/v2/metrics/query/descriptors',
                'metrics_timeseries': '/api/v2/metrics/query/timeseries',
                'metrics_timeseries_descriptors': '/api/v2/metrics/query/timeseries/descriptors',
                'metrics_timeseries_aggregates': '/api/v2/metrics/query/timeseries/aggregate',
                'entities': '/api/v2/entities',
                'problems': '/api/v2/problems',
                'events': '/api/v2/events',
                'synthetic_locations': '/api/v2/synthetic/locations',
                'synthetic_tests': '/api/v2/synthetic/executions',
                'synthetic_tests_results': '/api/v2/synthetic/tests/results'}

v2_params = {'metrics':
                 {'nextPageKey': 'nextPageKey',
                  'metricSelector': 'metricSelector',
                  'text': 'text',
                  'fields': ['fields'],
                  'writtenSince': 'writtenSince',
                  'metadataSelector': 'metadataSelector'},
             'metrics_query':
                 {'metricSelector': 'metricSelector',
                  'resolution': 'resolution',
                  'entitySelector': 'entitySelector',
                  'mzSelector': 'mzSelector',
                  'from': 'from',
                  'to': 'to'},
             'entities': {'entitySelector': 'type("HOST", "APPLICATION", "SERVICE", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE")'}}


# Get current working directory


def get_current_working_directory():
    """Get the current working directory.

    Returns:
        str: Current working directory.
    """
    return os.getcwd()


# Create managed uri given domain and environment id


def get_dynatrace_managed_uri(domain, environment_id):
    """Create a managed URI given the domain and environment ID.

    Args:
        domain (str): Dynatrace domain.
        environment_id (str): Dynatrace environment ID.

    Returns:
        str: Managed URI.
    """
    return dynatrace_managed_uri_v2.format(your_domain=domain, your_environment_id=environment_id)


# Create SaaS uri given environment id


def get_dynatrace_saas_uri(environment_id):
    """Create a SaaS URI given the environment ID.

    Args:
        environment_id (str): Dynatrace environment ID.

    Returns:
        str: SaaS URI.
    """
    return dynatrace_saas_uri_v2.format(your_environment_id=environment_id)


# Create environment active gate uri given domain and environment id


def get_dynatrace_environment_active_gate_uri(domain, environment_id):
    """Create an environment active gate URI given the domain and environment ID.

    Args:
        domain (str): Dynatrace domain.
        environment_id (str): Dynatrace environment ID.

    Returns:
        str: Environment active gate URI.
    """
    return dynatrace_environment_active_gate_v2.format(your_domain=domain, your_environment_id=environment_id)


# Parse secrets.env file


def parse_secrets_env():
    """Parse the secrets.env file. Only used for testing, and running the scripts locally.

    Returns:
        dict: Dictionary of secrets from the secrets.env file.
    """
    # Create the secrets dictionary
    secrets = {}
    print("Current working dir:", get_current_working_directory())
    # Check if the secrets.env file exists
    # Get the path to the current script

    # Construct a path relative to the script directory
    secrets_file = os.path.join(package_dir, 'secrets.env')
    print("Secrets file:", secrets_file)
    if os.path.exists(secrets_file):
        with open(secrets_file) as f:
            for line in f:
                (key, val) = line.split('=')
                secrets[key] = val.strip()
    return secrets


# Get dynatrace Problems from apiv2
# https://www.dynatrace.com/support/help/dynatrace-api/environment-api/problems/problems-get/

def get_dynatrace_metrics_descriptors(tenant, api_token, metric_selector, time=None, page_size=100, verify=True):
    """Get Dynatrace metrics descriptors from the API v2.

    Args:
        tenant (str): Dynatrace
        api_token (str): Dynatrace API token
        metric_selector (str): Metric selector.
        time (str): Time range for the problems. Defaults to None.
        page_size (int): Number of problems to return. Defaults to 100.

    Returns: 
        json: JSON response from the API.
    """
    # Set the headers
    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }
    # Set the parameters
    if time is None:
        parameters = {
            'metricSelector': metric_selector,
            'pageSize': page_size
        }
    else:
        parameters = {
            'metricSelector': metric_selector,
            'from': time,
            'pageSize': page_size
        }
    # Set the URL
    url = tenant + '/api/v2/metrics/query/descriptors'
    # Get the problems
    response = requests.get(url, headers=headers, params=parameters, verify=verify)
    # Return the response
    return response.json()


def default_time():
    written_since = (datetime.datetime.now() - datetime.timedelta(minutes=1)).timestamp()
    last_hour = {'written_since': f'{written_since}'}
    return last_hour


def get_from_time(minutes: int = 60) -> int:
    """Calculate unix stamp n minutes ago. Return unix epoch time in milliseconds with no decimals"""
    from_time = (datetime.datetime.now() - datetime.timedelta(minutes=minutes)).timestamp()

    # Round to nearest millisecond
    from_time = round(from_time * 1000)

    # Return the time
    return from_time


def get_dynatrace_data(endpoint, tenant, api_token, params={}, time=None, page_size=100, verify=True, opt_helper=None):
    """Get Dynatrace data from the API v2. 

    Args:
        endpoint (str): Dynatrace API endpoint.
        tenant (str): Dynatrace tenant URL.
        api_token (str): Dynatrace API token
        params (dict): Parameters for the API call. Defaults to {}.
        time (str): Time range for the problems. Defaults to None.
        page_size (int): Number of problems to return. Defaults to 100.
        verify (bool): Verify SSL certificate. Defaults to True.

    Yields:
        json: JSON response from the API.
    """

    parameters = {}
    results = {}
    parsed_response = {}
    selector = v2_selectors[endpoint]
    endpoint = v2_endpoints[endpoint]
    # Set the headers
    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }
    results = {}

    # Check if selector is metrics, if so, use 'writtenSince' instead of 'from' as the time parameter
    # Dyantrace uses different time parameters for different endpoints
    if time is not None:
        if selector == 'metrics':
            parameters['writtenSince'] = str(time)
        else:
            parameters['from'] = str(time)

    if selector == 'metrics':
        parameters['fields'] = 'unit,aggregationTypes'

    # Add page size to parameters
    parameters['pageSize'] = page_size

    # Concatenate the parameters, probably not useful at the moment, but could be in the future
    if params:
        parameters = {**params, **parameters}

    # Set the URL
    url = tenant + endpoint
    # Get the problems

    # Log all the things
    if opt_helper:
        opt_helper.log_debug(f'URL: {url}')
        opt_helper.log_debug(f'Headers: {headers}')
        opt_helper.log_debug(f'Params: {params}')
    try:
        response = requests.get(url, headers=headers, params=parameters, verify=verify)
        # If request doesn't have a 400 or greater error
        if opt_helper:
            opt_helper.log_debug(f'Response: {response}')
        if response.status_code < 400:
            parsed_response = response.json()

            # Yield the first page of results
            yield parsed_response[selector]
    except requests.exceptions.HTTPError as err:
        print(err)
        if opt_helper:
            opt_helper.log_error(f'Error: {err}')

        # Keep paging through the results if they exist
    while 'nextPageKey' in parsed_response and parsed_response.get('nextPageKey') is not None:
        # Dynatrace API v2 requires ONLY the nextPageKey to be passed as a parameter
        parameters = {'nextPageKey': parsed_response.get('nextPageKey')}

        # Try to get the next page of results, if it fails, break out of the loop
        try:
            response = requests.get(url, headers=headers, params=parameters, verify=verify)
            parsed_response = response.json()
            yield parsed_response[selector]

        except requests.exceptions.HTTPError as err:
            print(err)
            if opt_helper:
                opt_helper.log_error(f'Error: {err}')
            break

        # Check if nextPageKey is in the response or is null
        # Need to do this because Python doesn't have a do-while loop
        if 'nextPageKey' not in parsed_response or parsed_response.get('nextPageKey') is None:
            break


def prepare_dynatrace_request(endpoint_name, tenant, api_token, params={}, time=None, page_size=None,
                              entity_types=None):
    endpoint_uri = v2_endpoints[endpoint_name]
    selector = v2_selectors[endpoint_name]
    url = tenant + endpoint_uri
    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }
    prepared_params = {
        **params,
        **({'fields': 'unit,aggregationTypes'} if 'metrics' in selector else {}),
        **({'writtenSince': str(time)} if 'metrics' in selector and time else {'from': str(time)} if time else {}),
    }
    if page_size:
        prepared_params['pageSize'] = page_size

    if endpoint_name == 'entities' and entity_types:
        return [(url, headers, {**prepared_params, 'entitySelector': f'type("{entity_type}")'}, selector) for entity_type in
                entity_types]

    return [(url, headers, prepared_params, selector)]



def get_dynatrace_data(requests_info, verify=True, opt_helper=None):
    combined_results = []

    for url, headers, params, selector in requests_info:
        for response in _get_dynatrace_data(url, headers, params, verify, opt_helper):
            parsed_response = response[selector]
            for item in parsed_response:
                combined_results.append(item)

    return combined_results



def _get_dynatrace_data(url, headers, params, verify, opt_helper):
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, verify=verify)
            if opt_helper:
                opt_helper.log_debug(f'Response: {response.text}')
            response.raise_for_status()
            parsed_response = response.json()
            if opt_helper:
                opt_helper.log_debug(f'Parsed response: {parsed_response}')
            yield parsed_response

            if 'nextPageKey' not in parsed_response or parsed_response['nextPageKey'] is None:
                break
            params = {}
            params['nextPageKey'] = parsed_response['nextPageKey']

        except requests.exceptions.HTTPError as err:
            print(err)
            if opt_helper:
                opt_helper.log_error(f'Error: {err}')
            break




def get_metric_descriptors(tenant, api_token, verify=True):
    """Get all metric descriptors from the Dynatrace API v2.

    Args:
        tenant (str): Dynatrace tenant URL.
        api_token (str): Dynatrace API token.
        verify (bool): Verify SSL certificate. Defaults to True.

    Returns:
        dict: JSON response from the API containing all metric descriptors.
    """
    endpoint = v2_endpoints['metrics_descriptors']
    url = tenant + endpoint
    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }
    response = requests.get(url, headers=headers, verify=verify)
    if response.status_code < 400:
        return response.json()
    else:
        print('Error retrieving metric descriptors:', response.content)
        return None


import requests


def query_timeseries_data(metric_id, tenant, api_token, start_time, end_time, resolution='1min', verify=True):
    """Query timeseries data for a specific metric from the Dynatrace API v2.

    Args:
        metric_id (str): The ID of the metric to query.
        tenant (str): Dynatrace tenant URL.
        api_token (str): Dynatrace API token.
        start_time (str): The start time of the query in ISO 8601 format.
        end_time (str): The end time of the query in ISO 8601 format.
        resolution (str): The resolution of the data. Defaults to '1min'.
        verify (bool): Verify SSL certificate. Defaults to True.

    Returns:
        dict: JSON response from the API containing timeseries data.
    """
    endpoint = '/api/v2/metrics/query'
    url = tenant + endpoint
    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }
    query = {
        'queryMode': 'series',
        'metricSelector': 'metricId:{}'.format(metric_id),
        'resolution': resolution,
        'startTimestamp': start_time,
        'endTimestamp': end_time
    }
    response = requests.get(url, headers=headers, json=query, verify=verify)
    if response.status_code < 400:
        return response.json()
    else:
        print('Error querying timeseries data:', response.content)
        return None


# Assign secrets to variables
# dynatrace_tenant = os.environ['dynatrace_tenant']
# dynatrace_api_token = os.environ['dynatrace_api_token']


v2_selectors = {'metrics': 'metrics',
                'entities': 'entities',
                'problems': 'problems',
                'events': 'events',
                'synthetic_locations': 'locations',
                'synthetic_tests': 'synthetic/executions',
                'synthetic_nodes': 'synthetic/monitors',
                'metrics_query': 'result'}

# secrets = parse_secrets_env()
# dynatrace_tenant = secrets['dynatrace_tenant']
# dynatrace_api_token = secrets['dynatrace_api_token']

def parse_metric_selector(metric_selectors):
    """Parse a list of metric selectors into a string for the API call.

    Args:
        metric_selectors (list): A list of metric selectors.

    Returns:
        str: A string of metric selectors.
    """
    metric_selector = ''
    for selector in metric_selectors:
        metric_selector += selector + '\n'

    return metric_selector[:-1]


def parse_metric_selectors(file_path):
    # Parses the metric selectors from the given file path, and returns them as a list of strings.
    parsed_metric_selectors = []
    current_line = ""

    with open(file_path, 'r') as f:
        for line in f:
            stripped_line = line.strip()
            if not stripped_line:
                continue  # Ignore empty lines

            # If the line starts with a non-whitespace character, it's a new metric selector
            if line[0] != ' ' and line[0] != '\t':
                if current_line:
                    parsed_metric_selectors.append(current_line)
                current_line = stripped_line
            else:
                # If the line starts with a whitespace character, it's a continuation of the previous line
                current_line += " " + stripped_line

    if current_line:  # Add the last metric selector
        parsed_metric_selectors.append(current_line)

    return parsed_metric_selectors


def parse_metric_selectors_text_area(textarea_input):
    # Parses the metric selectors from the given textarea input, and returns them as a list of strings.
    parsed_metric_selectors = []
    current_line = ""

    # Split textarea input into lines
    lines = textarea_input.splitlines()

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue  # Ignore empty lines

        # If the line starts with a non-whitespace character, it's a new metric selector
        if line[0] != ' ' and line[0] != '\t':
            if current_line:
                parsed_metric_selectors.append(current_line)
            current_line = stripped_line
        else:
            # If the line starts with a whitespace character, it's a continuation of the previous line
            current_line += stripped_line

    if current_line:  # Add the last metric selector
        parsed_metric_selectors.append(current_line)

    return parsed_metric_selectors


# Usage example:
# file_path = 'metric_selectors.txt'
# parsed_metric_selectors = parse_metric_selectors(file_path)

# Print parsed metric selectors:
# for metric_selector in parsed_metric_selectors:
#     print(metric_selector)
