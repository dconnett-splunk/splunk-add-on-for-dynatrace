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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""util.py: This module contains utility functions for the package. These functions are used by the package's scripts.
    
    Functions:
        get_dynatrace_tenant: Get the Dynatrace tenant from the input.
        get_dynatrace_api_token: Get the Dynatrace API token from the input.
        get_dynatrace_collection_interval: Get the Dynatrace collection interval from the input.
        get_dynatrace_entity_cursor: Get the Dynatrace entity cursor from the input.
        get_dynatrace_entity_end"""

__author__ = "David Connett"
__version__ = "0.1.0"
__maintainer__ = "David Connett"
__email__ = "dconnett@splunk.com"
__status__ = "Development"
__license__ = "Splunk General Terms"

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
                'synthetic_tests': '/api/v2/synthetic/tests',
                'synthetic_tests_results': '/api/v2/synthetic/tests/results'}

v2_params = {'metrics':
             {'nextPageKey': 'nextPageKey',
              'metricSelector': 'metricSelector',
              'text': 'text',
              'fields': ['fields'],
              'writtenSince': 'writtenSince',
              'metadataSelector': 'metadataSelector'}}

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
    print(get_current_working_directory())
    # Check if the secrets.env file exists
    if os.path.exists('../../secrets.env'):
        # Open the secrets.env file
        with open('../../secrets.env') as f:
            # Loop through each line
            for line in f:
                # Split the line into key/value pairs
                (key, val) = line.split('=')
                # Add the key/value pair to the secrets dictionary
                secrets[key] = val.strip()
    # Return the secrets
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

def get_from_time(minutes=60):
    """Calculate unix stamp n minutes ago. Return unix epoch time in milliseconds with no decimals"""
    from_time = (datetime.datetime.now() - datetime.timedelta(minutes=minutes)).timestamp()

    # Round to nearest millisecond
    from_time = round(from_time * 1000)

    # Return the time
    return from_time


def get_dynatrace_data(endpoint, tenant, api_token, params={}, time=None, page_size=100, verify=True):
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
    try:
        response = requests.get(url, headers=headers, params=parameters, verify=verify)
        # If request doesn't have a 400 or greater error
        if response.status_code < 400:
            parsed_response = response.json()

            # Yield the first page of results
            yield parsed_response[selector]
    except requests.exceptions.HTTPError as err:
        print(err)

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
            break

        # Check if nextPageKey is in the response or is null
        # Need to do this because Python doesn't have a do-while loop
        if 'nextPageKey' not in parsed_response or parsed_response.get('nextPageKey') is None:
            break

# Assign secrets to variables
#dynatrace_tenant = os.environ['dynatrace_tenant']
#dynatrace_api_token = os.environ['dynatrace_api_token']




v2_selectors = {'metrics': 'metrics',
'entities': 'entities',
'problems': 'problems',
'events': 'events',
'synthetic_locations': 'locations'}

# secrets = parse_secrets_env()
# dynatrace_tenant = secrets['dynatrace_tenant']
# dynatrace_api_token = secrets['dynatrace_api_token']