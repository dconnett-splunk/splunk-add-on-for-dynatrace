import os
import datetime
import urllib3
from pathlib import Path
import shutil
import filecmp
import math

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
                'metric_descriptors': '/api/v2/metrics/{id}',
                'metrics_timeseries': '/api/v2/metrics/query/timeseries',
                'metrics_timeseries_descriptors': '/api/v2/metrics/query/timeseries/descriptors',
                'metrics_timeseries_aggregates': '/api/v2/metrics/query/timeseries/aggregate',
                'entities': '/api/v2/entities',
                'entity': '/api/v2/entities/{id}',
                'problems': '/api/v2/problems',
                'events': '/api/v2/events',
                'synthetic_locations': '/api/v2/synthetic/locations',
                'synthetic_tests_on_demand': '/api/v2/synthetic/executions',
                'synthetic_test_on_demand': '/api/v2/synthetic/executions/{id}/fullReport',
                'synthetic_monitors_http': '/api/v1/synthetic/monitors',
                'synthetic_monitor_http': '/api/v1/synthetic/monitors/{id}',
                'synthetic_monitors_http_v2': '/api/v2/synthetic/execution',

                # TODO Change SUCCESS to Parameter for status, need to get both FAILED and SUCCESS
                'synthetic_monitor_http_v2': '/api/v2/synthetic/execution/{id}/SUCCESS',
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
             'entities': {
                 'entitySelector': 'type("HOST", "APPLICATION", "SERVICE", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE")'}}

# These selectors are used to parse the response from the Dynatrace API.
# AKA The top level key in the map returned by the API.
v2_selectors = {'metrics': 'metrics',
                'metric_descriptors': 'metricId',
                'entities': 'entities',
                'entity': 'entities',
                'problems': 'problems',
                'events': 'events',
                'synthetic_locations': 'locations',
                'synthetics_on_demand': 'executions',
                'synthetic_monitors_http': 'monitors',
                'synthetic_monitor_http': 'entityId',
                'synthetic_monitor_http_v2': 'monitorId',
                'synthetic_tests_on_demand': 'executions',
                'synthetic_test_on_demand': 'entityId',
                'synthetic_nodes': 'monitors',
                'metrics_query': 'result'}


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


def parse_url(url):
    if not url.startswith('https://'):
        if url.startswith('http://'):
            return url.replace('http://', 'https://')
        else:
            return 'https://' + url
    return url

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


def default_time():
    written_since = (datetime.datetime.now() - datetime.timedelta(minutes=1)).timestamp()
    last_hour = {'written_since': f'{written_since}'}
    return last_hour


def get_from_time(minutes: int = 60) -> int:
    """Calculate unix stamp n minutes ago. Return unix epoch time in milliseconds with no decimals"""
    from_time = (datetime.datetime.now() - datetime.timedelta(minutes=minutes)).timestamp()

    # Round to nearest millisecond
    from_time = math.floor(from_time * 1000)

    # Return the time
    return from_time


def default_time_utc():
    written_since = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).timestamp()
    last_hour = {'written_since': written_since}
    return last_hour


def get_from_time_utc(minutes: int = 60) -> int:
    """Calculate unix stamp n minutes ago in UTC. Return unix epoch time in milliseconds with no decimals"""
    from_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)).timestamp()

    # Round to nearest millisecond
    from_time = math.floor(from_time * 1000)

    # Return the time
    return from_time



def create_session(tenant, api_token, verify=True):
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Api-Token {api_token}',
        'version': 'Splunk_TA_Dynatrace'
    })
    session.verify = verify
    session.base_url = tenant
    return session


def prepare_dynatrace_request(endpoint_name, tenant, api_token, params={}, time=None, page_size=None,
                              entity_types=None):
    endpoint_uri = v2_endpoints[endpoint_name]
    selector = v2_selectors[endpoint_name]
    url = tenant + endpoint_uri

    # Handle entity endpoint, fix this ugly hack later
    if endpoint_name == 'entity':
        # Format string replace id in endpoint_uri
        url = url.format(id=params['entity_id'])
        # Remove entity_id from params
        params.pop('entity_id')

    # Handle synthetic monitor endpoint, wildcard the suffix
    elif 'synthetic_monitor_http' in endpoint_name:
        url = url.format(id=params['entityId'])
        params.pop('entityId')

    elif 'synthetic_test_on_demand' in endpoint_name:
        url = url.format(id=params['executionId'])
        params.pop('executionId')

    elif 'metric_descriptors' in endpoint_name:
        url = url.format(id=params['metricSelector'])
        params.pop('metricSelector')

    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }

    # TODO Not PEP8 compliant, need to really clean this up
    prepared_params = {
        **params,
        **({'fields': 'unit,aggregationTypes'} if 'metrics' in selector else {}),
        **({'writtenSince': str(time)} if 'metrics' in selector and time else {
            'from': str(time)} if time and endpoint_name != 'synthetic_tests_on_demand' else {}),
        **({'schedulingFrom': str(time)} if endpoint_name == 'synthetic_tests_on_demand' and time else {}),
    }
    if page_size:
        prepared_params['pageSize'] = page_size

    if endpoint_name == 'entities' and entity_types:
        return [(url, headers, {**prepared_params, 'entitySelector': f'type("{entity_type}")'}, selector) for
                entity_type in
                entity_types]

    return [(url, headers, prepared_params, selector)]


def remove_sensitive_info_recursive(data, keys_to_remove):
    if isinstance(data, dict):
        data = {key: remove_sensitive_info_recursive(value, keys_to_remove) for key, value in data.items()
                if key not in keys_to_remove}
    elif isinstance(data, list):
        data = [remove_sensitive_info_recursive(item, keys_to_remove) for item in data]
    return data


def get_dynatrace_data(session, requests_info, opt_helper=None):
    for url, headers, params, selector in requests_info:
        for response in _get_dynatrace_data(session, url, headers, params, opt_helper):
            parsed_response = parse_dynatrace_response(response, selector)
            if parsed_response:
                return parsed_response
    return []


def parse_dynatrace_response(response, selector):
    resolution = None
    unit = None
    # Check if the response has an entityId, if so, return early, this is for entities endpoint
    if 'entityId' in response and isinstance(response, dict):
        return response
    # Check if monitorId is a top level key, return immediately if so this is for synthetic endpoint
    elif 'monitorId' in response and isinstance(response, dict):
        return response

    # This next line grabs a specific key from the response, if it doesn't exist, it returns the response
    parsed_response = response.get(selector, response)

    # Add resolution to parsed response if it exists: this is metric specific code
    # parsed response is a list and resolution is a string
    if 'result' in selector and isinstance(parsed_response, list) and parsed_response:
        parsed_response[0]['resolution'] = response.get('resolution')

    # Check if the parsed response is a list, if so, return early
    if isinstance(parsed_response, list):
        return parsed_response

    return None


def _get_dynatrace_data(session, url, headers, params, opt_helper):
    while True:
        try:
            response = session.get(url, headers=headers, params=params)

            if opt_helper:
                opt_helper.log_debug(f'Response: {response.text}')
            response.raise_for_status()
            response_json = response.json()
            if opt_helper:
                opt_helper.log_debug(f'Parsed response: {response_json}')
            yield response_json

            if 'nextPageKey' not in response_json or response_json['nextPageKey'] is None:
                break
            params = {'nextPageKey': response_json['nextPageKey']}

        except requests.exceptions.HTTPError as err:
            if opt_helper:
                opt_helper.log_error(f'Error: {err}')
            yield None
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


# secrets = parse_secrets_env()
# dynatrace_tenant = secrets['dynatrace_tenant']
# dynatrace_api_token = secrets['dynatrace_api_token']


def get_ssl_certificate_verification(helper):
    # Certificate code
    local_dir = os.path.abspath(os.path.join(Path(__file__).resolve().parent.parent, "local"))
    helper.log_debug('local_dir: {}'.format(local_dir))
    cert_file = os.path.join(local_dir, "cert.pem")
    helper.log_debug('cert_file: {}'.format(cert_file))
    user_uploaded_certificate = helper.get_global_setting('user_certificate')

    # Check if local user_certificate file, exists, is the same as the one in the UI, if not update the file on disk
    if os.path.isfile(cert_file):
        if user_uploaded_certificate:
            if not filecmp.cmp(cert_file, user_uploaded_certificate):
                helper.log_debug('Updating cert.pem')
                shutil.copy(user_uploaded_certificate, cert_file)

    helper.log_debug('user_uploaded_certificate: {}'.format(user_uploaded_certificate))

    # Set the default Splunk Cert store location $SPLUNK_HOME/etc/auth/
    splunk_cert_dir = os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'auth')

    if os.path.isfile(cert_file):
        opt_ssl_certificate_verification = cert_file
    # Check for user_uploaded_certificate
    elif os.path.isfile(user_uploaded_certificate):
        opt_ssl_certificate_verification = user_uploaded_certificate
    # Default to True if no valid file is found
    else:
        opt_ssl_certificate_verification = True

    return opt_ssl_certificate_verification

# Usage example:
# file_path = 'metric_selectors.txt'
# parsed_metric_selectors = parse_metric_selectors(file_path)

# Print parsed metric selectors:
# for metric_selector in parsed_metric_selectors:
#     print(metric_selector)
