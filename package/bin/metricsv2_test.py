import datetime
import json
import os
import sys
import time
from pathlib import Path

import package.bin.metrics_util
import util
import requests
import metrics_util as dt_metrics


PAGE_SIZE = 100

# List of metric selectors to collect

util.get_current_working_directory()
# get time from one hour ago in UTC milliseconds
end_time = datetime.datetime.now().isoformat() + 'Z'
start_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat() + 'Z'
opt_dynatrace_collection_interval_minutes = start_time

secrets = util.parse_secrets_env()
opt_dynatrace_tenant = secrets['dynatrace_tenant']
opt_dynatrace_api_token = secrets['dynatrace_api_token']

minutes = 1000
time_range = util.get_from_time(minutes)

session = requests.Session()
opt_ssl_certificate_verification = True
session.verify = opt_ssl_certificate_verification
dynatrace_metric_selectors = 'builtin:host.cpu.usage:merge(0):avg'



for metric_selector in package.bin.metrics_util.parse_metric_selectors_text_area(dynatrace_metric_selectors):

    end_time = f"{datetime.datetime.now().isoformat()}Z"
    start_time = f"{(datetime.datetime.now() - datetime.timedelta(minutes=opt_dynatrace_collection_interval_minutes)).isoformat()}Z"

    params = {'metricSelector': metric_selector, 'startTimestamp': start_time, 'endTimestamp': end_time,
              'pageSize': PAGE_SIZE}

    dynatrace_data = prepare_and_get_data('metrics_query', opt_dynatrace_tenant, opt_dynatrace_api_token,
                                          params, session, helper)

    metric_descriptor_data = prepare_and_get_data('metrics_descriptors', opt_dynatrace_tenant,
                                                  opt_dynatrace_api_token, {'metricSelector': metric_selector},
                                                  session, helper)

    for timeseries_data in dynatrace_data:
        if timeseries_data['data']:

            for item in process_timeseries_data(timeseries_data):
                event_data = build_event_data(item, timeseries_data, metric_descriptor_data,
                                              opt_dynatrace_tenant, metric_selector)
                serialized = json.dumps(event_data)
                #event = helper.new_event(data=serialized, time=item['timestamp'], index=index)
                #ew.write_event(event)
                print(serialized)


