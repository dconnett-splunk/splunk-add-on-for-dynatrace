from util import *
from datetime import datetime, timedelta
import time
from dynatrace_types import *
from itertools import *

# Get time one hour ago Human-readable format of 2021-01-25T05:57:01.123+01:00

get_current_working_directory()
# get time from one hour ago in UTC milliseconds
end_time = datetime.now().isoformat() + 'Z'
start_time = (datetime.now() - timedelta(hours=1)).isoformat() + 'Z'

secrets = parse_secrets_env()
dynatrace_tenant = secrets['dynatrace_tenant']
dynatrace_api_token = secrets['dynatrace_api_token']
print(f'dynatrace_tenant: {dynatrace_tenant}')
print(f'dynatrace_api_token: {dynatrace_api_token}')

minutes = CollectionInterval(1000)
time_range = get_from_time_utc(minutes)

session = create_session(dynatrace_tenant, dynatrace_api_token)


def test_synthetic_monitors():
    synthetic_monitor_http = prepare_dynatrace_params(Endpoint.SYNTHETIC_MONITORS_HTTP, dynatrace_api_token,
                                                      dynatrace_tenant)

    # Fetch the data using the prepared request information
    synthetic_monitor_http = get_dynatrace_data(session, synthetic_monitor_http)

    for test in synthetic_monitor_http:
        print(test)

    for monitor in synthetic_monitor_http:
        requests_info = prepare_dynatrace_params(Endpoint.SYNTHETIC_MONITOR_HTTP_V2, dynatrace_api_token,
                                                 dynatrace_tenant)
        monitor_http_results = get_dynatrace_data(session, requests_info)
        # print(monitor_http_results)

        # Find all keys in the dictionary named responseBody and delete them
        # Delete all responseBody keys and values from monitor_http_results
        # The path in the dictionary is locationsExecutionResults requestResults responseBody

        keys_to_remove = ['responseBody', 'peerCertificateDetails']
        print(remove_sensitive_info_recursive(monitor_http_results, keys_to_remove))


# On Demand Executions
# Get all the on demand executions

def test_on_demand_executions():
    on_demand_executions = prepare_dynatrace_params(Endpoint.SYNTHETIC_TESTS_ON_DEMAND, dynatrace_api_token,
                                                    dynatrace_tenant)
    on_demand_executions = get_dynatrace_data(session, on_demand_executions)
    # print(on_demand_executions)

    execution_ids = []
    for execution in on_demand_executions:
        execution_ids.append(execution['executionId'])

    for execution_id in execution_ids:
        on_demand_execution_request_info = prepare_dynatrace_params(Endpoint.SYNTHETIC_TESTS_ON_DEMAND,
                                                                    dynatrace_api_token, dynatrace_tenant)
        on_demand_execution = get_dynatrace_data(session, on_demand_execution_request_info)
        keys_to_remove = ['responseBody', 'peerCertificateDetails']
        print(remove_sensitive_info_recursive(on_demand_execution, keys_to_remove))


# Store requests:entityId in a list
# entity_ids = []
# for request in monitor_http_results['requests']:
#     entity_ids.append(request['entityId'])
# print(entity_ids)

# for each entity id, get the request details(
# for entity_id in entity_ids:
#     synthetic_monitor_http_steps = prepare_dynatrace_request('synthetic_monitor_http_v2',
#                                                          dynatrace_tenant,
#                                                          dynatrace_api_token,
#                                                          params={'entityId': entity_id})
#     synthetic_monitor_http_steps = get_dynatrace_data(synthetic_monitor_http_steps, verify=False)
#     print(synthetic_monitor_http_steps)


page_size = 4
entity_types = ['HOST', 'PROCESS_GROUP_INSTANCE', 'PROCESS_GROUP', 'APPLICATION', 'SERVICE']
requests_info = prepare_dynatrace_params(Endpoint.ENTITIES, dynatrace_api_token, dynatrace_tenant)

# Fetch the data using the prepared request information
entities_list = get_dynatrace_data(session, requests_info)

# Print the fetched data
for entity in entities_list:
    print(entity['entityId'])
    entity_info = get_dynatrace_data(session,
                                     prepare_dynatrace_params(Endpoint.ENTITY, dynatrace_api_token, dynatrace_tenant))
    print(entity_info)




# Testing new data collection functions
metrics_request_info = prepare_dynatrace_params(Endpoint.METRICS, dynatrace_api_token, dynatrace_tenant)

stored_metrics = []
metrics = get_dynatrace_data(session, metrics_request_info)
for metric in metrics:
    print(metric)
    stored_metrics.append(metric)

problems_requests_info = prepare_dynatrace_params(Endpoint.PROBLEMS, dynatrace_api_token, dynatrace_tenant)

problems = get_dynatrace_data(session, problems_requests_info)

for problem in problems:
    print(problem)

events_requests_info = prepare_dynatrace_params(Endpoint.EVENTS, dynatrace_api_token, dynatrace_tenant)

events = get_dynatrace_data(session, events_requests_info)
for event in events:
    print(event)

synthetic_locations = prepare_dynatrace_params(Endpoint.SYNTHETIC_LOCATIONS, dynatrace_api_token, dynatrace_tenant)

locations = get_dynatrace_data(session, synthetic_locations)
for location in locations:
    print(location)

# Print variables for testing
print('dynatrace_tenant: ' + dynatrace_tenant)
print('dynatrace_api_token: ' + dynatrace_api_token)
common_headers = {
    'Authorization': 'Api-Token {}'.format(dynatrace_api_token),
    'version': 'Splunk_TA_Dynatrace'
}
parameters = {
    'from': time.time() - 3600,
    'pageSize': page_size
}

{**common_headers, **parameters}

# Trying to get metrics from Dynatrace API v2
end_time = datetime.now().isoformat() + 'Z'
start_time = (datetime.now() - timedelta(hours=1)).isoformat() + 'Z'


metrics_request_info = prepare_dynatrace_params(Endpoint.METRICS, dynatrace_api_token, dynatrace_tenant)

metrics = get_dynatrace_data(session, metrics_request_info)
metric_ids = []
for metric in metrics:
    print(metric['metricId'])
    print(metric['unit'])
    metric_ids.append(metric['metricId'])

metrics_params = {
    'startTimestamp': start_time,
    'endTimestamp': end_time
}

for metric_id in metric_ids:
    metrics_params['metricSelector'] = metric_id
    metrics_request_info = prepare_dynatrace_params(Endpoint.METRICS_QUERY, dynatrace_api_token, dynatrace_tenant)

    metric_descriptors_request_info = prepare_dynatrace_params(Endpoint.METRIC_DESCRIPTORS, dynatrace_api_token,
                                                               dynatrace_tenant)

    metric_descriptors_request_info = get_dynatrace_data(session, metric_descriptors_request_info)

    metric_descriptors_request_info = prepare_dynatrace_request('metrics_descriptors',
                                                         dynatrace_tenant,
                                                         dynatrace_api_token,
                                                         params={'metricSelector': metric_id})

    metric_descriptors_request_info = get_dynatrace_data(metric_descriptors_request_info, dynatrace_tenant, dynatrace_api_token)

    print("Metrics request info: " + str(metrics_request_info))

    metrics = get_dynatrace_data(session, metrics_request_info)
    for metric in metrics:
        # Zip timestamps and data
        if metric['data']:
            print("Metric data and dimensions", metric['data'][0]['dimensions'])
            # if there is more than one metric, print the whole metric
            if len(metric['data'][0]['values']) > 1:
                print("Metric:", metric)
            series = zip(metric['data'][0]['timestamps'], metric['data'][0]['values'])


# print('Timeseries test')
# timeseries = get_dynatrace_data('metrics_query', dynatrace_tenant, dynatrace_api_token, time=get_from_time(1000),
#                                 verify=False, params=metrics_params)

# Dynatrace problem headers


# TODO: 403 Forbidden from entity types and entities, get more privileges from Dynatrace

# print ssl certificate from dynatrace entity

# Autehnticate to Dynatrace API v2
session.close()
