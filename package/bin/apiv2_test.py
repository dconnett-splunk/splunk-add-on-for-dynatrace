from package.bin.util import *
import datetime
# Get time one hour ago Human-readable format of 2021-01-25T05:57:01.123+01:00

# get time from one hour ago in UTC milliseconds

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

for page in metrics:
    for metric in page:
        print(metric)


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

# Dynatrace problem headers


# TODO: 403 Forbidden from entity types and entities, get more privileges from Dynatrace

# print ssl certificate from dynatrace entity

# Autehnticate to Dynatrace API v2