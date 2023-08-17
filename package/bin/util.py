import os
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pickle
import urllib3
from pathlib import Path
import shutil
import filecmp
import math
import requests
from enum import Enum
from dataclasses import dataclass
from urllib.parse import quote_plus
from requests import Response, Request, PreparedRequest, Session
import re
import string
from dynatrace_types_37 import *
# from dynatrace_types import *
import json
import certifi
from string import Formatter

#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""util.py: This module contains utility functions for the package. These functions are used by the package's scripts.

    Functions:
        get_dynatrace_tenant: Get the Dynatrace tenant from the input.
        get_dynatrace_api_token: Get the Dynatrace API token from the input.
        get_dynatrace_collection_interval: Get the Dynatrace collection interval from the input.
        get_dynatrace_entity_cursor: Get the Dynatrace entity cursor from the input.
        get_dynatrace_entity_end"""

__author__ = "David Connett"
__version__ = "2.1.1"
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
    url_path_param: Optional[PathParam]
    extra_params: Optional[List[str]] = None


class Endpoint(Enum):
    METRICS = \
        EndpointInfo(
            URL('/api/v2/metrics'),
            ResponseSelector('metrics'),
            Params({'writtenSince': '{time}',
                    'fields': 'unit,aggregationTypes'}),
            None)
    METRICS_QUERY = \
        EndpointInfo(
            URL('/api/v2/metrics/query'),
            ResponseSelector('result'),
            Params({'metricSelector': '{metricSelector}'}),
            None)
    METRIC_DESCRIPTORS = \
        EndpointInfo(
            URL('/api/v2/metrics/{metricKey}'),
            ResponseSelector('metricId'),
            None,
            PathParam('metricKey'))
    ENTITIES = \
        EndpointInfo(
            URL('/api/v2/entities'),
            ResponseSelector('entities'),
            Params({'entitySelector': 'type(\"{entitySelector}\")'}),
            None,
            ["HOST", "PROCESS_GROUP_INSTANCE", "PROCESS_GROUP", "APPLICATION", "SERVICE", "SYNTHETIC_TEST",
             "SYNTHETIC_TEST_STEP"])
    ENTITY = \
        EndpointInfo(
            URL('/api/v2/entities/{entityId}'),
            ResponseSelector("entityId"),
            None,
            PathParam('entityId'))
    PROBLEM = \
        EndpointInfo(
            URL('/api/v2/problems/{problemId}'),
            ResponseSelector('problemId'),
            None,
            PathParam('problemId'))
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
            Params({'schedulingFrom': '{time}'}),
            None)
    SYNTHETIC_TEST_ON_DEMAND = \
        EndpointInfo(
            URL('/api/v2/synthetic/executions/{executionId}/fullReport'),
            ResponseSelector('entityId'),
            None,
            PathParam('executionId'))
    SYNTHETIC_MONITORS_HTTP = \
        EndpointInfo(
            URL('/api/v1/synthetic/monitors'),
            ResponseSelector('monitors'),
            None,
            None)
    SYNTHETIC_MONITOR_HTTP = \
        EndpointInfo(
            URL('/api/v1/synthetic/monitors/{entityId}'),
            ResponseSelector('entityId'),
            None,
            PathParam('entityId'))
    SYNTHETIC_MONITOR_HTTP_V2 = \
        EndpointInfo(
            URL('/api/v2/synthetic/execution/{monitorId}'),
            ResponseSelector('monitorId'),
            None,
            PathParam('monitorId'),
            ["SUCCESS", "FAILED"])
    # This is a hack because SYNTHETIC_MONITORS_HTTP returns entityIds and others return monitorIds
    SYNTHETIC_MONITOR_ENTITY_V2 = \
        EndpointInfo(
            URL('/api/v2/synthetic/execution/{entityId}'),
            ResponseSelector('entityId'),
            None,
            PathParam('entityId'),
            ["SUCCESS", "FAILED"])
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
    def url_path_param(self):
        return self.value.url_path_param if isinstance(self.value, EndpointInfo) else None

    @property
    def extra_params(self):
        return self.value.extra_params

    @classmethod
    def get_endpoint(cls, endpoint_value):
        try:
            return cls[endpoint_value]
        except KeyError:
            return None


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


def endpoint_enum_lookup(url: str) -> Optional[EndpointInfo]:
    """Match a URL to an EndpointInfo object."""
    for endpoint in Endpoint:
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
                if not line.startswith('#'):
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


def find_format_key(value: str) -> Optional[str]:
    """Find the key to be formatted from a given string value."""
    format_keys = [tup[1] for tup in Formatter().parse(value) if tup[1] is not None]
    return format_keys[0] if format_keys else None


def get_formatted_key_value_pair(key: str, value: str, params: Params) -> Tuple[str, Any]:
    """Return the key-value pair after formatting."""
    replaced_key = find_format_key(value)
    if replaced_key and replaced_key in params:
        formatted_value = value.format(**{replaced_key: params[replaced_key]})
        return key, formatted_value
    return key, value


def format_url_and_pop_path_params(endpoint: Endpoint, url: URL, params: Params) -> Tuple[URL, Params]:
    """Format the URL and pop the URL Path parameter from the params dictionary."""
    # print('format_url_and_pop_path_params: {}'.format(endpoint)
    #         + ' url: {}'.format(url)
    #         + ' params: {}'.format(params))
    if endpoint.url_path_param:
        endpoint_path_key = endpoint.url_path_param
        if endpoint_path_key in params:
            formatted_url = URL(url.format(**{endpoint_path_key: params[endpoint_path_key]}))
            new_params = Params({k: v for k, v in params.items() if k != endpoint_path_key})
            # print('format_url_and_pop_path_params: {}'.format(formatted_url)
            #         + ' new_params: {}'.format(new_params))
            return formatted_url, new_params
    return url, params


def format_params(endpoint: Endpoint, params: Params) -> Params:
    """Format and inject parameters according to the Endpoint Enum.
    Injects default parameters from V2Endpoints Enum,
                Params Input: {}
                -> {'fields': 'unit,aggregationTypes'} for METRICS,
    Formats default parameters from V2Endpoints Enum (if it exists)
                Params Input: {'entitySelector': 'HOST'}
                V2Endpoint Input: {'entitySelector': 'type(\"{entitySelector}\")'}
                -> {'entitySelector': 'type('HOST')'},
    Renames parameters with the same meaning from the V2Endpoints Enum,
                Params Input: {'time': 1234}
                V2Endpoints Input: {'writtenSince': '{time}'}
                 -> {'writtenSince': '1234'}

    Why? Different API endpoints need specific inputs, but many are actually the same data and just need to be renamed,
    or some endpoints always need the same inputs all the time.

    Cleaner idea: defining functions or classes for each endpoint would probably be a better idea,
    but this design was chosen because of the evolution of the code over time. This is a hack, but it works... for now.

    Important to know:
        1. If you pass a parameter that changes names, the old one will be removed {time} -> {writtenSince}
        2. Parameters that have a format string will be formatted with the input params of the same key name
            {'entitySelector': 'HOST'}
            {'entitySelector': 'type(\"{entitySelector}\")'}
                -> {'entitySelector': 'type(\"HOST\")'}

    """
    formatted_params = params.copy()
    if endpoint.params:
        for key, value in endpoint.params.items():
            # If the value contains a format string
            if '{' in value:
                format_key = find_format_key(value)
                if format_key and format_key in formatted_params:
                    new_key, new_value = get_formatted_key_value_pair(key, value, formatted_params)
                    formatted_params[new_key] = new_value
                    # If the key has changed, remove the original key
                    if new_key != key:
                        formatted_params.pop(key)
                    # If the formatted value uses a parameter, consume that parameter
                    if format_key != key:
                        formatted_params.pop(format_key)
            else:
                formatted_params[key] = value
    return Params(formatted_params)


def build_url(endpoint: Endpoint, tenant: Tenant, params: Params) -> URL:
    url = URL(tenant + endpoint.url)
    url, params = format_url_and_pop_path_params(endpoint, url, params)
    return URL(url)


def prepare_dynatrace_headers(api_token, extra_headers=None):
    headers = {
        'Authorization': f'Api-Token {api_token}',
        'version': f'Splunk_TA_Dynatrace {__version__}',
    }
    return {**headers, **extra_headers} if extra_headers else headers


def prepare_dynatrace_params(base_url, endpoint: Endpoint, params, extra_params=None):
    """Prepare a Dynatrace request for the given endpoint and parameters.
    Params that are expected:
        time

    """
    endpoint_url = endpoint.url
    url = base_url + endpoint_url
    url, prepared_params = format_url_and_pop_path_params(endpoint, url, params)

    if endpoint == Endpoint.ENTITIES and extra_params:
        for entity_type in extra_params:
            prepared_params['entitySelector'] = entity_type
            yield url, format_params(endpoint, prepared_params), endpoint
    elif endpoint == Endpoint.METRICS_QUERY and extra_params:
        for metric_selector in extra_params:
            prepared_params['metricSelector'] = metric_selector
            yield url, format_params(endpoint, prepared_params), endpoint
    elif endpoint == Endpoint.METRICS and extra_params:
        # {'metricSelector': 'builtin:host.cpu.usage:merge(0):avg, metricselector2, etc...'}
        prepared_params['metricSelector'] = ','.join(extra_params)
        yield url, format_params(endpoint, prepared_params), endpoint
    elif endpoint == Endpoint.SYNTHETIC_MONITOR_HTTP_V2 and endpoint.extra_params:
        for extra_param in endpoint.extra_params:  # loop through ["SUCCESS", "FAILURE"]
            result_url = url + "/" + extra_param  # Append the suffix
            yield result_url, format_params(endpoint, params), endpoint
    elif endpoint == Endpoint.SYNTHETIC_MONITOR_ENTITY_V2 and endpoint.extra_params:
        for extra_param in endpoint.extra_params:  # loop through ["SUCCESS", "FAILURE"]
            result_url = url + "/" + extra_param  # Append the suffix
            yield result_url, format_params(endpoint, params), endpoint
    else:
        yield url, format_params(endpoint, params), endpoint


def prepare_dynatrace_request(session: Session, url: URL, params: Params):
    session.url = url
    session.params = params
    return session.prepare_request(Request('GET', url, params=params))


def remove_sensitive_info_recursive(data, keys_to_remove):
    if isinstance(data, dict):
        data = {key: remove_sensitive_info_recursive(value, keys_to_remove) for key, value in data.items()
                if key not in keys_to_remove}
    elif isinstance(data, list):
        data = [remove_sensitive_info_recursive(item, keys_to_remove) for item in data]
    return data

def execute_session(endpoints: Union[Endpoint, Tuple[Endpoint, Endpoint]], tenant, api_token, params, extra_params=None,
                    opt_helper=None):
    params = Params(params)

    with requests.Session() as session:
        prepared_headers = prepare_dynatrace_headers(api_token)
        session.headers.update(prepared_headers)

        # Check if a single endpoint or a list of endpoints was provided
        if isinstance(endpoints, tuple):
            main_endpoint = endpoints[0]
            detail_endpoints = endpoints[1:]
        else:
            main_endpoint = endpoints
            detail_endpoints = []

        # Process the main endpoint
        if main_endpoint.extra_params and extra_params is None:
            extra_params = main_endpoint.extra_params

        prepared_params_list = prepare_dynatrace_params(tenant, main_endpoint, params, extra_params)

        for result in get_dynatrace_data(session, prepared_params_list, opt_helper):
            # Check if result is a list and if so, yield each item individually
            # Only do this if there are no detail endpoints
            if not detail_endpoints and isinstance(result, list):
                for item in result:
                    yield item
            elif not detail_endpoints:
                yield result

            # Process the detailed endpoints, if any
            for endpoint in detail_endpoints:
                if result:
                    for record in result:
                        id = record[endpoint.selector]
                        params = Params({'time': get_from_time(),
                                         endpoint.url_path_param: id})
                        prepared_params_list = prepare_dynatrace_params(tenant, endpoint, params, extra_params)
                        for details in get_dynatrace_data(session, prepared_params_list):
                            yield details


def get_dynatrace_data(session: Session, prepared_params_list, opt_helper=None):
    for url, params, endpoint in prepared_params_list:
        prepared_request = prepare_dynatrace_request(session, url, params)
        settings = session.merge_environment_settings(prepared_request.url, {}, None, get_ssl_certificate_verification(), None)
        # print('prepared_request: {}'.format(prepared_request))
        # print('prepared_request.url: {}'.format(prepared_request.url))
        # print('params: {}'.format(params))
        # print('settings: {}'.format(settings))

        if opt_helper:
            opt_helper.log_debug(f'Prepared Request: {prepared_request} {prepared_request.url} {prepared_request.body}')
            opt_helper.log_debug(f'url: {url}')
            opt_helper.log_debug(f'headers: {prepared_request.headers}')
            opt_helper.log_debug(f'params: {params}')
            opt_helper.log_debug(f'Settings: {settings}')

        for response_json in _get_dynatrace_data(session, prepared_request, settings, opt_helper):
            parsed_response = parse_dynatrace_response(response_json, endpoint)

            if opt_helper:
                opt_helper.log_debug(f'Parsed Response: {parsed_response}')

            if parsed_response:
                yield parsed_response


def _get_dynatrace_data(session, prepared_request: PreparedRequest, settings: dict, opt_helper) -> json:
    base_url = prepared_request.url.replace(prepared_request.path_url, '')
    while True:
        try:
            response: Response = session.send(prepared_request, **settings)
            response.raise_for_status()  # raise HTTPError if status >=400

            if opt_helper:
                opt_helper.log_debug(f'Response: {response.text}')

            response_json: json = response.json()

            if opt_helper:
                opt_helper.log_debug(f'Parsed response: {response_json}')

            yield response_json

            if 'nextPageKey' not in response_json or response_json['nextPageKey'] is None:
                break

            # Re-prepare the URL using the updated params
            prepared_request.prepare_url(base_url, {'nextPageKey': response_json['nextPageKey']})

        except requests.exceptions.HTTPError as err:
            if opt_helper:
                # Log the status code and error message
                opt_helper.log_error(f'HTTP Error: {err}')

                # If the server sent a response, log the response body
                if err.response is not None:
                    opt_helper.log_error(f'Details: {err.response.text}')
            break

        except Exception as e:
            if opt_helper:
                opt_helper.log_error(f'Unexpected error: {e}')
            break


def parse_dynatrace_response(response: json, endpoint: Endpoint):
    resolution = None
    unit = None
    selector = endpoint.selector
    # Check if the response has an entityId, if so, return early, this is for entities endpoint
    if endpoint == Endpoint.ENTITIES and isinstance(response, dict):
        return response.get(selector, response)
    # Check if monitorId is a top level key, return immediately if so this is for synthetic endpoint
    elif endpoint == Endpoint.SYNTHETIC_MONITOR_HTTP_V2 and isinstance(response, dict):
        return response
    # elif endpoint == Endpoint.SYNTHETIC_MONITORS_HTTP_V2:
    #     return SyntheticOnDemandExecution(**response)
    elif endpoint == Endpoint.METRIC_DESCRIPTORS and isinstance(response, dict):
        return MetricDescriptor(**response)
    elif endpoint == Endpoint.ENTITY and isinstance(response, dict):
        return Entity(**response)
    elif endpoint == Endpoint.PROBLEM and isinstance(response, dict):
        return Problem(**response)
    elif endpoint == Endpoint.METRICS_QUERY and isinstance(response, dict):
        return MetricData(**response)
    elif endpoint == Endpoint.METRICS and isinstance(response, dict):
        return MetricDescriptorCollection(**response)


    # This next line grabs a specific key from the response, if it doesn't exist, it returns the response
    parsed_response = response.get(selector, response)

    # Add resolution to parsed response if it exists: this is metric specific code
    # parsed response is a list and resolution is a string
    # Probably don't need this anymore
    if endpoint == Endpoint.METRICS_QUERY and isinstance(parsed_response, list) and parsed_response:
        parsed_response: MetricData = MetricData(**response)
        return parsed_response

    # Check if the parsed response is a list, if so, return early
    if isinstance(parsed_response, list):
        return parsed_response

    return response


def get_ssl_certificate_verification(helper=None):
    local_dir = os.path.abspath(os.path.join(Path(__file__).resolve().parent.parent, "local"))
    if helper:
        helper.log_debug('local_dir: {}'.format(local_dir))
    cert_file = os.path.join(local_dir, "cert.pem")
    if helper:
        helper.log_debug('cert_file: {}'.format(cert_file))

    user_uploaded_certificate = helper.get_global_setting('user_certificate') if helper else None

    # Check if local user_certificate file exists, is the same as the one in the UI, if not update the file on disk
    if os.path.isfile(cert_file) and user_uploaded_certificate and not filecmp.cmp(cert_file, user_uploaded_certificate):
        if helper:
            helper.log_debug('Updating cert.pem')
        shutil.copy(user_uploaded_certificate, cert_file)

    if helper:
        helper.log_debug('user_uploaded_certificate: {}'.format(user_uploaded_certificate))

    # This is commented out for now, as requested
    # if 'SPLUNK_HOME' in os.environ:
    #     splunk_cert_dir = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'auth')
    #     os.environ['REQUESTS_CA_BUNDLE'] = splunk_cert_dir
    # else:
    #     if helper:
    #         helper.log_warning('$SPLUNK_HOME environment variable is not set.')

    # Check if cert_file exists first, otherwise use certifi.where() as default
    if os.path.isfile(cert_file):
        opt_ssl_certificate_verification = cert_file
    elif user_uploaded_certificate and os.path.isfile(user_uploaded_certificate):
        opt_ssl_certificate_verification = user_uploaded_certificate
    else:
        opt_ssl_certificate_verification = certifi.where()

    return opt_ssl_certificate_verification



