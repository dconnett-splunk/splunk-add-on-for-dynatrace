from package.bin.util import *
import datetime
# Get time one hour ago Human-readable format of 2021-01-25T05:57:01.123+01:00

# get time from one hour ago in UTC milliseconds

written_since = (datetime.datetime.now() - datetime.timedelta(minutes=1)).timestamp()
paged_data = get_dynatrace_data('metrics', dynatrace_tenant, dynatrace_api_token, page_size=500, verify=False)

secrets = parse_secrets_env()
dynatrace_tenant = secrets['dynatrace_tenant']
dynatrace_api_token = secrets['dynatrace_api_token']

written_since = (datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp()
last_hour = {'written_since': f'{written_since}'}
written_since = (datetime.datetime.now() - datetime.timedelta(hours=200)).timestamp()
last_week = {'written_since': f'{written_since}'}
print(last_hour)

# Testing new data collection functions
get_dynatrace_data('metrics', dynatrace_tenant, dynatrace_api_token, params=last_hour, time=None, page_size=100, verify=False)
get_dynatrace_data('problems', dynatrace_tenant, dynatrace_api_token, page_size=100, verify=False)
get_dynatrace_data('events', dynatrace_tenant, dynatrace_api_token, params=last_hour,  time=None, page_size=100, verify=False)
get_dynatrace_data('synthetic_locations', dynatrace_tenant, dynatrace_api_token, params=last_hour, time=None, page_size=100, verify=False)

paged_data = get_dynatrace_data(v2_endpoints['metrics'], dynatrace_tenant, dynatrace_api_token, time=None, page_size=100, verify=False)
# Get next page field from paged_data
del paged_data['nextPageKey']
paged_data['nextPageKey']
next_page
paged_data
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

problems: json = get_dynatrace_problems(dynatrace_tenant, dynatrace_api_token, verify=False)
entities: json = get_dynatrace_entity(dynatrace_tenant, dynatrace_api_token, verify=False)
metrics: json = get_all_dynatrace_metrics(
    dynatrace_tenant, dynatrace_api_token, verify=False)

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