import os
import sys
import time
import datetime
import json





bin_dir = os.path.basename(__file__)

'''
'''
import import_declare_test

import os
import os.path as op
import sys
import time
import datetime
import json

import traceback
import requests
from splunklib import modularinput as smi
from solnlib import conf_manager
from solnlib import log
from solnlib.modular_input import checkpointer
from splunktaucclib.modinput_wrapper import base_modinput  as base_mi 
import requests
import util



bin_dir = os.path.basename(__file__)

'''
'''


# encoding = utf-8


'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''


class ModInputdynatrace_timeseries_metrics_v2(base_mi.BaseModInput):

    def __init__(self):
        use_single_instance = False
        super(ModInputdynatrace_timeseries_metrics_v2, self).__init__(
            "splunk_ta_dynatrace", "dynatrace_timeseries_metrics_v2", use_single_instance)
        self.global_checkbox_fields = None

    def get_scheme(self):
        """overloaded splunklib modularinput method"""
        scheme = super(ModInputdynatrace_timeseries_metrics_v2,
                       self).get_scheme()
        scheme.title = ("Dynatrace Timeseries Metrics API v2")
        scheme.description = (
            "Go to the add-on\'s configuration UI and configure modular inputs under the Inputs menu.")
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True

        scheme.add_argument(smi.Argument("name", title="Name",
                                         description="",
                                         required_on_create=True))

        """
        For customized inputs, hard code the arguments here to hide argument detail from users.
        For other input types, arguments should be get from input_module. Defining new input types could be easier.
        """
        scheme.add_argument(smi.Argument("dynatrace_account", title="Dynatrace Account",
                                         description="",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("dynatrace_collection_interval", title="Dynatrace Collection Interval",
                                         description="Relative timeframe passed to Dynatrace API. Timeframe of data to be collected at each polling interval.",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("dynatrace_metric_selectors_v2_textarea", title="Dynatrace Metric Selectors",
                                         description="",
                                         required_on_create=True,
                                         required_on_edit=False))

        return scheme

    def get_app_name(self):
        return "Splunk_TA_Dynatrace"

    def validate_input(helper, definition):
        """Implement your own validation logic to validate the input stanza configurations"""
        # This example accesses the modular input variable
        # dynatrace_tenant = definition.parameters.get('dynatrace_tenant', None)
        # dynatrace_api_token = definition.parameters.get('dynatrace_api_token', None)
        # dynatrace_collection_interval = definition.parameters.get('dynatrace_collection_interval', None)
        pass

    def collect_events(helper, ew):
        ''' Updated for Splunk 8 '''
        '''SSL Verification'''

        # Log the start of the collect_events function
        helper.log_debug('Beginning collect_events')

        # opt_ssl_certificate_verification = helper.get_arg('ssl_certificate_verification')
        opt_ssl_certificate_verification = True

        # Retrieve Dynatrace account information
        dynatrace_account_input = helper.get_arg("dynatrace_account")
        dynatrace_tenant_input = dynatrace_account_input["username"]
        opt_dynatrace_api_token = dynatrace_account_input["password"]
        index = helper.get_arg("index")

        # Ensure the Dynatrace tenant URL starts with 'https://'
        if dynatrace_tenant_input.startswith('https://'):
            opt_dynatrace_tenant = dynatrace_tenant_input
        elif dynatrace_tenant_input.startswith('http://'):
            opt_dynatrace_tenant = dynatrace_tenant_input.replace('http://', 'https://')
        else:
            opt_dynatrace_tenant = 'https://' + dynatrace_tenant_input

        # Log the verify_ssl value
        helper.log_debug('verify_ssl: {}'.format(opt_ssl_certificate_verification))

        # Retrieve Dynatrace collection interval and other arguments
        opt_dynatrace_collection_interval_minutes = int(helper.get_arg("dynatrace_collection_interval"))
        opt_dynatrace_collection_interval = int(helper.get_arg('dynatrace_collection_interval'))
        opt_dynatrace_entity_endpoints = helper.get_arg('entity_endpoints')
        opt_ssl_certificate_verification = helper.get_arg('ssl_certificate_verification')
        dynatrace_metric_selectors = helper.get_arg('dynatrace_metric_selectors_v2_textarea')

        # Log all previously retrieved arguments
        helper.log_debug('dynatrace_tenant: {}'.format(opt_dynatrace_tenant))
        helper.log_debug('dynatrace_collection_interval: {}'.format(opt_dynatrace_collection_interval))
        helper.log_debug('dynatrace_collection_interval_minutes: {}'.format(opt_dynatrace_collection_interval_minutes))
        helper.log_debug('dynatrace_metric_selectors: {}'.format(dynatrace_metric_selectors))



        COUNT = 'COUNT'
        AVERAGE = 'AVG'
        hecTime = 0

        service_metrics_avg = ['com.dynatrace.builtin:app.useractionduration',
                                'com.dynatrace.builtin:service.responsetime',
                                'com.dynatrace.builtin:service.failurerate'
                              ]
        service_metrics_count = ['com.dynatrace.builtin:app.apdex',
                            'com.dynatrace.builtin:app.useractionsperminute',
                            'com.dynatrace.builtin:service.requestspermin'
                          ]
        process_metrics = ['com.dynatrace.builtin:pgi.cpu.usage',
                            'com.dynatrace.builtin:pgi.mem.usage',
                            'com.dynatrace.builtin:pgi.nic.bytesreceived',
                            'com.dynatrace.builtin:pgi.nic.bytessent',
                            'com.dynatrace.builtin:pgi.suspension',
                            'com.dynatrace.builtin:pgi.workerprocesses'
                          ]

        host_metrics = ['com.dynatrace.builtin:host.cpu.idle',
                            'com.dynatrace.builtin:host.cpu.iowait',
                            'com.dynatrace.builtin:host.cpu.other',
                            'com.dynatrace.builtin:host.cpu.steal',
                            'com.dynatrace.builtin:host.cpu.system',
                            'com.dynatrace.builtin:host.cpu.user',
                            'com.dynatrace.builtin:host.mem.used',
                            'com.dynatrace.builtin:host.mem.pagefaults',
                            'com.dynatrace.builtin:host.nic.bytesreceived',
                            'com.dynatrace.builtin:host.nic.bytessent',
                            'com.dynatrace.builtin:host.nic.packetsreceived',
                            'com.dynatrace.builtin:host.nic.packetsreceiveddropped',
                            'com.dynatrace.builtin:host.nic.packetsreceivederrors',
                            'com.dynatrace.builtin:host.nic.packetssentdropped',
                            'com.dynatrace.builtin:host.nic.packetssenterrors',
                            'com.dynatrace.builtin:host.disk.readtime',
                            'com.dynatrace.builtin:host.disk.writetime',
                            'com.dynatrace.builtin:host.disk.freespacepercentage',
                            'com.dynatrace.builtin:host.disk.availablespace',
                            'com.dynatrace.builtin:host.disk.usedspace'
                          ]

        synthetic_metrics = ['com.dynatrace.builtin:webcheck.availability',
                              'com.dynatrace.builtin:webcheck.performance.actionduration']


        # Get textbox metrics input
        # dynatrace_metric_selectors = helper.get_arg('dynatrace_metric_selectors_v2_textarea')
        # for metric_selector in util.parse_metric_selectors_text_area(dynatrace_metric_selectors):
        #     print(metric_selector)
        #     helper.log_info("Processing Metric Selector: %s" % metric_selector)

        for metric_selector in util.parse_metric_selectors_text_area(dynatrace_metric_selectors):
            helper.log_debug("Processing Metric Selector: %s" % metric_selector)

            # Set up parameters for the API call

            # Trying to get metrics from Dynatrace API v2
            end_time = datetime.datetime.now().isoformat() + 'Z'
            start_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat() + 'Z'

            params = {
                'metricSelector': metric_selector,
                'startTimestamp': start_time,
                'endTimestamp': end_time,
                'pageSize': 100
            }

            # Prepare the Dynatrace request
            requests_info = util.prepare_dynatrace_request('metrics_query',
                                                           opt_dynatrace_tenant,
                                                           opt_dynatrace_api_token,
                                                           params=params)

            # Get Dynatrace data using the 'get_dynatrace_data' function from util.py
            dynatrace_data = util.get_dynatrace_data(requests_info,
                                                     verify=opt_ssl_certificate_verification,
                                                     opt_helper=helper)

            def process_timeseries_data(timeseries_data):
                for entry in timeseries_data['data']:
                    dimensions = entry['dimensions']
                    timestamps = entry['timestamps']
                    values = entry['values']
                    dimension_map = entry['dimensionMap']

                    for timestamp, value in zip(timestamps, values):
                        item = dimension_map.copy()
                        item['timestamp'] = timestamp
                        item['value'] = value

                        for dim_name, dim_value in zip(dimension_map.keys(), dimensions):
                            item[dim_name] = dim_value

                        yield item

            for timeseries_data in dynatrace_data:
                if timeseries_data['data']:
                    helper.log_debug("Processing Metric: %s" % timeseries_data['metricId'])
                    helper.log_debug("Writing data to index: %s" % index)

                    for item in process_timeseries_data(timeseries_data):
                        metric_type, metric_name = timeseries_data['metricId'].split(':', 1)
                        metric_value = item['value']
                        timestamp = item['timestamp']

                        event_data = {
                            'metric_name': timeseries_data['metricId'],
                            'value': metric_value,
                            'dynatraceTenant': opt_dynatrace_tenant,
                            'metricSelector': metric_selector,
                        }

                        for key, value in item.items():
                            if key not in event_data:
                                event_data[key] = value

                        if 'unit' in timeseries_data:
                            event_data['unit'] = timeseries_data['unit']

                        serialized = json.dumps(event_data)
                        event = helper.new_event(
                            data=serialized,
                            time=timestamp,
                            index=index,
                        )

                        ew.write_event(event)

    def get_account_fields(self):
        account_fields= []
        account_fields.append("dynatrace_account")
        return account_fields

    def get_checkbox_fields(self):
        checkbox_fields= []
        checkbox_fields.append("ssl_certificate_verification")
        return checkbox_fields

    def get_global_checkbox_fields(self):
        if self.global_checkbox_fields is None:
            checkbox_name_file= os.path.join(bin_dir, 'global_checkbox_param.json')
            try:
                if os.path.isfile(checkbox_name_file):
                    with open(checkbox_name_file, 'r') as fp:
                        self.global_checkbox_fields= json.load(fp)
                else:
                    self.global_checkbox_fields= []
            except Exception as e:
                self.log_error(
                    'Get exception when loading global checkbox parameter names. ' + str(e))
                self.global_checkbox_fields= []
        return self.global_checkbox_fields

if __name__ == "__main__":
    exitcode= ModInputdynatrace_timeseries_metrics_v2().run(sys.argv)
    sys.exit(exitcode)
