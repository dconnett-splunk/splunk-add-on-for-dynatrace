from util import *
import datetime
from itertools import *

# Get time one hour ago Human-readable format of 2021-01-25T05:57:01.123+01:00

get_current_working_directory()
# get time from one hour ago in UTC milliseconds
end_time = datetime.datetime.now().isoformat() + 'Z'
start_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat() + 'Z'

secrets = parse_secrets_env()
dynatrace_tenant = secrets['dynatrace_tenant']
dynatrace_api_token = secrets['dynatrace_api_token']

minutes = 1000
# Testing new data collection functions
metrics = get_dynatrace_data('metrics',
                             dynatrace_tenant,
                             dynatrace_api_token,
                             time=get_from_time(minutes),
                             page_size=100,
                             verify=False)

stored_metrics = []
for page in metrics:
    for metric in page:
        print(metric)
        stored_metrics.append(metric)

problems = get_dynatrace_data('problems',
                              dynatrace_tenant,
                              dynatrace_api_token,
                              time=get_from_time(10000),
                              verify=False)

for page in problems:
    for problem in page:
        print(problem)

events = get_dynatrace_data('events',
                            dynatrace_tenant,
                            dynatrace_api_token,
                            time=get_from_time(minutes),
                            page_size=100,
                            verify=False)
for page in events:
    print(page)
    for event in page:
        print(event)

synthetic_locations = get_dynatrace_data('synthetic_locations',
                                         dynatrace_tenant,
                                         dynatrace_api_token,
                                         time=get_from_time(minutes),
                                         page_size=100,
                                         verify=False)
for page in synthetic_locations:
    print(page)
    for location in page:
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
    'pageSize': 100
}

{**common_headers, **parameters}

# Trying to get metrics from Dynatrace API v2
end_time = datetime.datetime.now().isoformat() + 'Z'
start_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat() + 'Z'

metrics = get_dynatrace_data('metrics', dynatrace_tenant, dynatrace_api_token, time=get_from_time(1000), page_size=100,
                             verify=False)
metric_ids = []
for page in metrics:
    for metric in page:
        print(metric['metricId'])
        metric_ids.append(metric['metricId'])

metrics_params = {
    'metricSelector': 'builtin:host.cpu.usage',
    'startTimestamp': start_time,
    'endTimestamp': end_time
}

for metric_id in metric_ids:
    metrics_params['metricSelector'] = metric_id
    metrics = get_dynatrace_data('metrics_query', dynatrace_tenant, dynatrace_api_token, time=get_from_time(1000),
                                 verify=False, params=metrics_params)
    for page in metrics:
        for metric in page:
            # Zip timestamps and data
            if metric['data']:
                print(metric['metricId'])
                series = zip(metric['data'][0]['timestamps'], metric['data'][0]['values'])
                for datapoint in series:
                    print(datapoint)

# print('Timeseries test')
# timeseries = get_dynatrace_data('metrics_query', dynatrace_tenant, dynatrace_api_token, time=get_from_time(1000),
#                                 verify=False, params=metrics_params)

# Dynatrace problem headers


# TODO: 403 Forbidden from entity types and entities, get more privileges from Dynatrace

# print ssl certificate from dynatrace entity

# Autehnticate to Dynatrace API v2
