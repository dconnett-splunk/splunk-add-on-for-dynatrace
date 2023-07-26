import os
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pickle
import urllib3
from pathlib import Path
import shutil
import filecmp
import math
from dynatrace_types import *
import requests
from enum import Enum
from dataclasses import dataclass
from urllib.parse import quote_plus
from requests import Response, Request, PreparedRequest, Session
import re

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

@dataclass
class EndpointInfo:
    url: URL
    selector: ResponseSelector
    params: Optional[Params]
    url_param_map: Optional[str]


class V2Endpoints(Enum):
    METRICS = \
        EndpointInfo(
            URL('/api/v2/metrics'),
            ResponseSelector('metrics'),
            Params({'nextPageKey': 'nextPageKey',
                    'metricSelector': 'metricSelector',
                    'text': 'text',
                    'fields': ['fields'],
                    'writtenSince': 'writtenSince',
                    'metadataSelector': 'metadataSelector'}),
            None)
    METRICS_QUERY = \
        EndpointInfo(
            URL('/api/v2/metrics/query'),
            ResponseSelector('result'),
            None,
            None)
    METRIC_DESCRIPTORS = \
        EndpointInfo(
            URL('/api/v2/metrics/{id}'),
            ResponseSelector('metricId'),
            None,
            'metricSelector')
    ENTITIES = \
        EndpointInfo(
            URL('/api/v2/entities'),
            ResponseSelector('entities'),
            Params({'entitySelector': 'type("HOST", "APPLICATION", "SERVICE", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE", SYNTHETIC_TEST", "SYNTHETIC_TEST_STEP")'}),
            None)
    ENTITY = \
        EndpointInfo(
            URL('/api/v2/entities/{id}'),
            ResponseSelector("entities"),
            None,
            'entity_id')
    PROBLEM = \
        EndpointInfo(
            URL('/api/v2/problems/{id}'),
            ResponseSelector('problem'),
            None,
            'problemId') # Not sure about this one
    PROBLEMS = \
        EndpointInfo(
            URL('/api/v2/problems'),
            ResponseSelector('problems'),
            None,
            None)
    EVENTS = \
        EndpointInfo(
            URL('/api/v2/events'),
            ResponseSelector('events'),
            None,
            None)
    SYNTHETIC_LOCATIONS = \
        EndpointInfo(
            URL('/api/v2/synthetic/locations'),
            ResponseSelector('locations'),
            None,
            None)
    SYNTHETIC_TESTS_ON_DEMAND = \
        EndpointInfo(
            URL('/api/v2/synthetic/executions'),
            ResponseSelector('executions'),
            None,
            None)
    SYNTHETIC_TEST_ON_DEMAND = \
        EndpointInfo(
            URL('/api/v2/synthetic/executions/{id}/fullReport'),
            ResponseSelector('entityId'),
            None,
            'executionId')
    SYNTHETIC_MONITORS_HTTP = \
        EndpointInfo(
            URL('/api/v1/synthetic/monitors'),
            ResponseSelector('monitors'),
            None,
            None)
    SYNTHETIC_MONITOR_HTTP = \
        EndpointInfo(
            URL('/api/v1/synthetic/monitors/{id}'),
            ResponseSelector('entityId'),
            None,
            'entityId')
    SYNTHETIC_MONITORS_HTTP_V2 = \
        EndpointInfo(
            URL('/api/v2/synthetic/execution'),
            ResponseSelector('executions'),
            None,
            None)
    SYNTHETIC_MONITOR_HTTP_V2 = \
        EndpointInfo(
            URL('/api/v2/synthetic/execution/{id}/SUCCESS'),
            ResponseSelector('monitorId'),
            None,
            'monitorId')
    SYNTHETIC_TESTS_RESULTS = \
        EndpointInfo(
            URL('/api/v2/synthetic/tests/results'),
            ResponseSelector('results'),
            None,
            None)

    @property
    def url(self):
        return self.value.url if isinstance(self.value, EndpointInfo) else self.value

    @property
    def selector(self):
        return self.value.selector if isinstance(self.value, EndpointInfo) else None

    @property
    def params(self):
        return self.value.params if isinstance(self.value, EndpointInfo) else None

    @property
    def url_param_map(self):
        return self.value.url_param_map if isinstance(self.value, EndpointInfo) else None


# These selectors are used to parse the response from the Dynatrace API.
# AKA The top level key in the map returned by the API.
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
# v2_selectors = {'metrics': 'metrics',
#                 'metric_descriptors': 'metricId',
#                 'entities': 'entities',
#                 'entity': 'entities',
#                 'problems': 'problems',
#                 'events': 'events',
#                 'synthetic_locations': 'locations',
#                 'synthetics_on_demand': 'executions',
#                 'synthetic_monitors_http': 'monitors',
#                 'synthetic_monitor_http': 'entityId',
#                 'synthetic_monitor_http_v2': 'monitorId',
#                 'synthetic_tests_on_demand': 'executions',
#                 'synthetic_test_on_demand': 'entityId',
#                 'synthetic_nodes': 'monitors',
#                 'metrics_query': 'result'}


def get_current_working_directory():
    """Get the current working directory.

    Returns:
        str: Current working directory.
    """
    return os.getcwd()


def get_dynatrace_managed_uri(domain, environment_id):
    """Create a managed URI given the domain and environment ID.

    Args:
        domain (str): Dynatrace domain.
        environment_id (str): Dynatrace environment ID.

    Returns:
        str: Managed URI.
    """
    return dynatrace_managed_uri_v2.format(your_domain=domain, your_environment_id=environment_id)


def get_dynatrace_saas_uri(environment_id):
    """Create a SaaS URI given the environment ID.

    Args:
        environment_id (str): Dynatrace environment ID.

    Returns:
        str: SaaS URI.
    """
    return dynatrace_saas_uri_v2.format(your_environment_id=environment_id)


def get_dynatrace_environment_active_gate_uri(domain, environment_id):
    """Create an environment active gate URI given the domain and environment ID.

    Args:
        domain (str): Dynatrace domain.
        environment_id (str): Dynatrace environment ID.

    Returns:
        str: Environment active gate URI.
    """
    return dynatrace_environment_active_gate_v2.format(your_domain=domain, your_environment_id=environment_id)


def get_endpoint_info(url: str) -> Optional[EndpointInfo]:
    """Match a URL to an EndpointInfo object."""
    for endpoint in V2Endpoints:
        endpoint_url_regex = re.escape(endpoint.value.url).replace(r"\{id\}", r"[^/]+")
        # Ensure endpoint.url is at the end of url
        endpoint_url_regex = r".*{}$".format(endpoint_url_regex)
        if re.search(endpoint_url_regex, url):
            return Optional[endpoint]
    return None


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


def default_time() -> WrittenSinceParam:
    written_since = (datetime.now() - timedelta(minutes=1)).timestamp()
    last_hour: WrittenSinceParam = WrittenSinceParam({'written_since': f'{written_since}'})
    return last_hour


def get_from_time(minutes: CollectionInterval = 60) -> int:
    """Calculate unix stamp n minutes ago. Return unix epoch time in milliseconds with no decimals"""
    from_time_float = (datetime.now() - timedelta(minutes=minutes)).timestamp()

    # Round to nearest millisecond
    from_time: int = math.floor(from_time_float * 1000)

    # Return the time
    return from_time


def calculate_utc_start_timestamp(minutes: Optional[int] = 60) -> StartTime:
    """Calculate unix timestamp n minutes ago in UTC"""
    now: datetime = datetime.utcnow()
    time_range: timedelta = timedelta(minutes=minutes)
    start_time: datetime = now - time_range
    timestamp: StartTime = StartTime(math.floor(start_time.timestamp() * 1000))

    return timestamp


def get_from_time_utc(minutes: Optional[int] = 60) -> int:
    """Calculate unix stamp n minutes ago in UTC. Return unix epoch time in milliseconds with no decimals"""
    from_time = calculate_utc_start_timestamp(minutes)

    # Return the time
    return from_time


def default_time_utc_written_since() -> WrittenSinceParam:
    """Return the current time in UTC minus 1 hour
    in unix epoch time in milliseconds with no decimals with the key written_since.
    This is for certain endpoints that require a time parameter in UTC"""
    last_hour: StartTime = calculate_utc_start_timestamp(60)
    written_since = WrittenSinceParam({'written_since': f'{last_hour}'})
    return written_since


def create_session(tenant, api_token, verify=True) -> requests.Session:
    session = requests.Session()
    session.verify = verify
    session.headers = {
        'Authorization': f'Api-Token {api_token}'
    }
    session.base_url = tenant
    return session


def format_url_and_pop_params(endpoint: V2Endpoints, params: dict, url: str) -> Tuple[str, dict]:
    """Format the URL and pop the URL Path parameter from the params dictionary.
    Why are we passing Path Parameters through the Query Parameters?
    No idea, but I feel like there was a reason..."""
    if endpoint.url_param_map:
        param_key = endpoint.url_param_map
        url = url.format(id=params[param_key])
        params.pop(param_key)
    return url, params


def prepare_dynatrace_request(endpoint: V2Endpoints, tenant, api_token, params=None, time=None, page_size=None,
                              entity_types=None):
    if params is None:
        params = {}

    endpoint_url = endpoint.url
    selector = endpoint.selector
    url = tenant + endpoint_url
    url, params = format_url_and_pop_params(endpoint, params, url)

    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }

    # TODO Written before Enums, might be able to use Enums here instead of strings
    prepared_params = {
        **params,
        **({'fields': 'unit,aggregationTypes'} if 'metrics' in selector else {}),
        **({'writtenSince': str(time)} if 'metrics' in selector and time else {
            'from': str(time)} if time and endpoint != V2Endpoints.SYNTHETIC_TESTS_ON_DEMAND else {}),
        **({'schedulingFrom': str(time)} if endpoint == V2Endpoints.SYNTHETIC_TESTS_ON_DEMAND and time else {}),
    }
    if page_size:
        prepared_params['pageSize'] = page_size

    # This is a hack because Dynatrace doesn't allow you to query for multiple entity types
    if endpoint == V2Endpoints.ENTITIES and entity_types:
        return [(url, headers, {**prepared_params, 'entitySelector': f'type("{entity_type}")'}, endpoint) for
                entity_type in
                entity_types]

    return [(url, headers, prepared_params, endpoint)]


def remove_sensitive_info_recursive(data, keys_to_remove):
    if isinstance(data, dict):
        data = {key: remove_sensitive_info_recursive(value, keys_to_remove) for key, value in data.items()
                if key not in keys_to_remove}
    elif isinstance(data, list):
        data = [remove_sensitive_info_recursive(item, keys_to_remove) for item in data]
    return data


def get_dynatrace_data(session, requests_info, opt_helper=None):
    for url, headers, params, endpoint in requests_info:
        for response_json in _get_dynatrace_data(session, url, headers, params, opt_helper):
            parsed_response = parse_dynatrace_response(response_json, endpoint)
            if parsed_response:
                return parsed_response
    return []


def _get_dynatrace_data(session, url, headers, params, opt_helper) -> json:
    while True:
        try:
            request: Request = requests.Request('GET', url, headers=headers, params=params)
            prepared_request: PreparedRequest = session.prepare_request(request)
            settings: dict = session.merge_environment_settings(prepared_request.url, {}, None, None, None)
            response: Response = session.send(prepared_request, **settings)

            if opt_helper:
                opt_helper.log_debug(f'Response: {response.text}')
            response.raise_for_status()
            response_json: json = response.json()
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


def parse_dynatrace_response(response: json, endpoint: V2Endpoints):
    resolution = None
    unit = None
    selector = endpoint.selector
    # Check if the response has an entityId, if so, return early, this is for entities endpoint
    if endpoint == V2Endpoints.ENTITIES in response and isinstance(response, dict):
        return response
    # Check if monitorId is a top level key, return immediately if so this is for synthetic endpoint
    elif endpoint == V2Endpoints.SYNTHETIC_MONITOR_HTTP_V2 and isinstance(response, dict):
        return MonitorExecutionResults(**response)
    elif endpoint == V2Endpoints.METRIC_DESCRIPTORS and isinstance(response, dict):
        return MetricDescriptor(**response)

    # This next line grabs a specific key from the response, if it doesn't exist, it returns the response
    parsed_response = response.get(selector, response)

    # Add resolution to parsed response if it exists: this is metric specific code
    # parsed response is a list and resolution is a string
    if endpoint == V2Endpoints.METRICS_QUERY and isinstance(parsed_response, list) and parsed_response:
        parsed_response: MetricData = MetricData(**response)
        return parsed_response

    # Check if the parsed response is a list, if so, return early
    if isinstance(parsed_response, list):
        return parsed_response

    return None



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

