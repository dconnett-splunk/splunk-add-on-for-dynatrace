import datetime
import json
import os
import sys
import time
from pathlib import Path
import util
import requests
import itertools
import re
from dynatrace_types import *

def prepare_and_get_data(api_type, tenant, token, params, session, helper):
    request_info = util.prepare_dynatrace_request(api_type, tenant, token, params=params)
    helper.log_debug(f"Request Info: {request_info}")
    data = util.get_dynatrace_data(session, request_info, opt_helper=helper)

    if data is None:
        helper.log_error(f"Failed to fetch data for request: {request_info}")
        # Handle the error as needed: retry, return early, raise exception, etc.

    return data


def process_timeseries_data(timeseries_data):
    for entry in timeseries_data['data']:
        dimensions = entry['dimensions']
        timestamps = entry['timestamps']
        values = entry['values']
        dimension_map = entry['dimensionMap']

        for timestamp, value in zip(timestamps, values):
            item = {**dimension_map, 'timestamp': timestamp, 'value': value,
                    **dict(zip(dimension_map.keys(), dimensions))}
            yield item


def build_event_data(item, timeseries_data, metric_descriptor_data, opt_dynatrace_tenant, metric_selector):
    event_data = {
        **item,
        **{'metric_name': timeseries_data['metricId'], 'value': item['value'],
           'dynatraceTenant': opt_dynatrace_tenant, 'metricSelector': metric_selector,
           'resolution': timeseries_data['resolution']},
        **({'unit': metric_descriptor_data['unit']} if 'unit' in metric_descriptor_data else {})
    }
    return event_data


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


def parse_metric_selector(metric_selectors: list[str]) -> MetricSelector:
    """Parse a list of metric selectors into a string for the API call.

    Args:
        metric_selectors (list): A list of metric selectors.

    Returns:
        MetricSelector: A string of metric selectors.
    """
    metric_selector_str = ''
    for selector in metric_selectors:
        metric_selector_str += selector + '\n'

    metric_selector = MetricSelector(metric_selector_str[:-1])

    return metric_selector


def parse_metric_selectors_from_file(file_path: Path):
    with open(file_path, 'r') as f:
        file_content = f.read()

    return parse_metric_selectors_text_area(file_content)


def parse_metric_selectors_text_area(textarea_input: str) -> list[MetricSelector]:
    """Scan line by line, if there is leading whitespace or tabs, it's a continuation of the previous line.
    Strip them and append them to the previous selector.
    @param textarea_input: The text area input
    @return: A list of metric selectors
    """

    # Combine the lines that are continuations of the previous line
    joined_sub_expressions = re.sub(re.compile(r'\n\s+:'), ':', textarea_input)

    # Split the lines into a list
    parsed_metric_selectors_str = joined_sub_expressions.splitlines()

    # Convert each string in the list to a MetricSelector
    parsed_metric_selectors = [MetricSelector(selector) for selector in parsed_metric_selectors_str]

    return parsed_metric_selectors

