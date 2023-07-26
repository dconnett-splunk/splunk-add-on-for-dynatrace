import os
import sys
import time
from datetime import datetime, timedelta
import json
from pathlib import Path

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
from tempfile import NamedTemporaryFile
import metrics_util




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
        helper.log_debug('Beginning collect_events')

        dynatrace_account_input = helper.get_arg("dynatrace_account")
        dynatrace_tenant_input = dynatrace_account_input["username"]
        opt_dynatrace_api_token = dynatrace_account_input["password"]
        index = helper.get_arg("index")

        opt_dynatrace_tenant = util.parse_url(dynatrace_tenant_input)

        opt_dynatrace_collection_interval_minutes = int(helper.get_arg("dynatrace_collection_interval"))
        dynatrace_metric_selectors = helper.get_arg('dynatrace_metric_selectors_v2_textarea')

        opt_ssl_certificate_verification = True

        helper.log_debug(f'verify_ssl: {opt_ssl_certificate_verification}')
        helper.log_debug(f'dynatrace_tenant: {opt_dynatrace_tenant}')
        helper.log_debug(f'dynatrace_collection_interval_minutes: {opt_dynatrace_collection_interval_minutes}')
        helper.log_debug(f'dynatrace_metric_selectors: {dynatrace_metric_selectors}')

        page_size = 100

        session = requests.Session()
        session.verify = opt_ssl_certificate_verification

        for metric_selector in metrics_util.parse_metric_selectors_text_area(dynatrace_metric_selectors):
            helper.log_debug(f"Processing Metric Selector: {metric_selector}")

            end_time = f"{datetime.datetime.now().isoformat()}Z"
            start_time = f"{(datetime.datetime.now() - datetime.timedelta(minutes=opt_dynatrace_collection_interval_minutes)).isoformat()}Z"

            params = {'metricSelector': metric_selector, 'startTimestamp': start_time, 'endTimestamp': end_time,
                      'pageSize': page_size}

            dynatrace_data = metrics_util.prepare_and_get_data('metrics_query', opt_dynatrace_tenant, opt_dynatrace_api_token,
                                                  params, session, helper)

            metric_descriptor_data = metrics_util.prepare_and_get_data('metrics_descriptors', opt_dynatrace_tenant,
                                                          opt_dynatrace_api_token, {'metricSelector': metric_selector},
                                                          session, helper)

            for timeseries_data in dynatrace_data:
                if timeseries_data['data']:
                    helper.log_debug(f"Processing Metric: {timeseries_data['metricId']}")
                    helper.log_debug(f"Writing data to index: {index}")

                    for item in metrics_util.flatten_and_zip_timeseries(timeseries_data):
                        event_data = metrics_util.build_event_data(item, timeseries_data, metric_descriptor_data,
                                                      opt_dynatrace_tenant, metric_selector)
                        serialized = json.dumps(event_data)
                        event = helper.new_event(data=serialized, time=item['timestamp'], index=index)

                        ew.write_event(event)

        session.close()


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
