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
        scheme.add_argument(smi.Argument("ssl_certificate_verification", title="SSL Certificate Verification",
                                         description="",
                                         required_on_create=False,
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
        helper.log_info('Beginning collect_events')

        ssl_certificate = helper.get_arg('ssl_certificate_verification')

        if ssl_certificate == True:
            verify_ssl = True
        else:
            verify_ssl = False

        helper.log_info('verify_ssl: {}'.format(verify_ssl))

        '''
        Force HTTPS
        '''

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
        dynatrace_metric_selectors = helper.get_arg('dynatrace_metric_selectors_v2_textarea')
        for metric_selector in util.parse_metric_selectors_text_area(dynatrace_metric_selectors):
            print(metric_selector)
            helper.log_info("Processing Metric Selector: %s" % metric_selector)



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
