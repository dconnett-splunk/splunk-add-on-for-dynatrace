import sys
import os
import json
import time
import datetime
from urllib import response
import requests
import traceback
import logging
import logging.handlers


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
    """Parse the secrets.env file.

    Returns:
        dict: Dictionary of secrets from the secrets.env file.
    """
    # Create the secrets dictionary
    secrets = {}
    # Check if the secrets.env file exists
    if os.path.exists('secrets.env'):
        # Open the secrets.env file
        with open('secrets.env') as f:
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
def get_dynatrace_problems(tenant, api_token, time=None, page_size=100):
    """Get Dynatrace problems from the API v2.

    Args:
        tenant (str): Dynatrace
        api_token (str): Dynatrace API token
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
            'pageSize': page_size
        }
    else:
        parameters = {
            'from': time,
            'pageSize': page_size
        }
    # Set the URL
    url = tenant + '/api/v2/problems'
    # Get the problems
    response = requests.get(url, headers=headers, params=parameters)
    # Return the response
    return response.json()

# Get all monitoried entity types


def get_dynatrace_entity_types(tenant, api_token):
    """Get all monitored entity types from the API v2.

    Args:
        tenant (str): Dynatrace tenant.
        api_token (str): Dynatrace API token.

    Returns:
        json: JSON response from the API.
    """
    # Set the headers
    headers = {
        'Authorization': 'Api-Token {}'.format(api_token),
        'version': 'Splunk_TA_Dynatrace'
    }
    # Set the URL
    url = tenant + '/api/v2/entityTypes'
    # Get the entity types
    response = requests.get(url, headers=headers)
    # Return the response
    return response.json()


def get_dynatrace_entity(tenant, api_token, time=None, page_size=100):
    """Get Dynatrace entities from the API v2.

    Args:
        tenant (str): Dynatrace
        api_token (str): Dynatrace API token
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
            'pageSize': page_size
        }
    else:
        parameters = {
            'from': time,
            'pageSize': page_size
        }
    # Set the URL
    url = tenant + '/api/v2/entities'
    # Get the problems
    response = requests.get(url, headers=headers, params=parameters)
    # Return the response
    return response.json()

# List all dynatrace entities


def get_all_dynatrace_entities(tenant, api_token, entity_selector, time=None, page_size=100):
    """Get all Dynatrace entities.

    Args:
        tenant (str): Dynatrace tenant.
        api_token (str): Dynatrace API token.
        entity_selector (str): Entity selector.
        time (str): Time range for the problems. Defaults to None.
        page_size (int): Number of problems to return. Defaults to 100.

    Returns:
        json: List of all Dynatrace entities.
    """
    # Create the list of entities
    entities = []
    # Get the first page of entities
    response = get_dynatrace_entity(
        tenant, api_token, time=time, page_size=page_size)
    # Loop through the entities
    for entity in response['values']:
        # Check if the entity matches the entity selector
        if entity_selector in entity['entityId']:
            # Add the entity to the list of entities
            entities.append(entity)
    # Get the next page of entities
    next_page = response['nextPageKey']
    # Loop while there is a next page
    while next_page is not None:
        # Get the next page of entities
        response = get_dynatrace_entity(
            tenant, api_token, time=time, page_size=page_size, next_page=next_page)
        # Loop through the entities
        for entity in response['values']:
            # Check if the entity matches the entity selector
            if entity_selector in entity['entityId']:
                # Add the entity to the list of entities
                entities.append(entity)
        # Get the next page of entities
        next_page = response['nextPageKey']
    # Return the entities
    return entities


# List all metrics
# https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/examples/list-all-metrics
def get_all_dynatrace_metrics(tenant, api_token, time=None, page_size=100):
    """Get Dynatrace metrics from the API v2.

    Args:
        tenant (str): Dynatrace 
        api_token (str): Dynatrace API token
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
            'pageSize': page_size
        }
    else:
        parameters = {
            'from': time,
            'pageSize': page_size
        }

    # Set the URL
    url = tenant + '/api/v2/metrics'

    # Add paramaters to get all metrics
    parameters['fields'] = 'displayName,unit,aggregationTypes'

    response = requests.get(url, headers=headers, params=parameters)

    # Return the response
    return response.json()


# Get Dynatrace metrics from api v2
def get_dynatrace_metrics(tenant, api_token, metric_selector, time=None, page_size=100):
    """Get Dynatrace metrics from the API v2.

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
    url = tenant + '/api/v2/metrics/query'
    # Get the problems
    response = requests.get(url, headers=headers, params=parameters)
    # Return the response
    return response.json()

# Get Dynatrace metrics descriptors from api v2


def get_dynatrace_metrics_descriptors(tenant, api_token, metric_selector, time=None, page_size=100):
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
    response = requests.get(url, headers=headers, params=parameters)
    # Return the response
    return response.json()


# Assign secrets to variables
#dynatrace_tenant = os.environ['dynatrace_tenant']
#dynatrace_api_token = os.environ['dynatrace_api_token']
secrets = parse_secrets_env()
dynatrace_tenant = secrets['dynatrace_tenant']
dynatrace_api_token = secrets['dynatrace_api_token']

# Print variables for testing
print('dynatrace_tenant: ' + dynatrace_tenant)
print('dynatrace_api_token: ' + dynatrace_api_token)
common_headers = {
    'Authorization': 'Api-Token {}'.format(dynatrace_api_token),
    'version': 'Splunk_TA_Dynatrace'
}
parameters = {
    'from': time.time() - 3600,
    'pageSize': 100
}


{**common_headers, **parameters}

# Dynatrace problem headers

print(get_dynatrace_entity(dynatrace_tenant, dynatrace_api_token))

# Store the metrics in a list

problems: json = get_dynatrace_problems(dynatrace_tenant, dynatrace_api_token)
entities: json = get_dynatrace_entity(dynatrace_tenant, dynatrace_api_token)
metrics: json = get_all_dynatrace_metrics(
    dynatrace_tenant, dynatrace_api_token)

print(problems)
print(entities)
print(metrics)

# List all metrics display names
for metric in metrics['metrics']:
    print(metric['displayName'])

print(get_dynatrace_entity_types(dynatrace_tenant, dynatrace_api_token))

# TODO: 403 Forbidden from entity types and entities, get more privileges from Dynatrace

# print ssl certificate from dynatrace entity

# Autehnticate to Dynatrace API v2
