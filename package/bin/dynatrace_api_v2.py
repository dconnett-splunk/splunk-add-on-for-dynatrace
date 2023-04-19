# SPDX-FileCopyrightText: 2023 David Connett
# SPDX-License-Identifier: Apache-2.0

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

# encoding = utf-8



class ModInputdynatrace_api_v2(base_mi.BaseModInput):

    def __init__(self):
        use_single_instance = False
        super(ModInputdynatrace_api_v2, self).__init__("splunk_ta_dynatrace", "dynatrace_api_v2", use_single_instance)
        self.global_checkbox_fields = None

    def get_scheme(self):
        """overloaded splunklib modularinput method"""
        scheme = super(ModInputdynatrace_api_v2, self).get_scheme()
        scheme.title = ("Dynatrace API v2")
        scheme.description = ("Go to the add-on\'s configuration UI and configure modular inputs under the Inputs menu.")
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

        scheme.add_argument(smi.Argument("dynatrace_apiv2_endpoint", title="Dynatrace API Endpoint",
                                         description="Dynatrace API endpoint to be used for data collection.",
                                         required_on_create=True,
                                         required_on_edit=False))

        # scheme.add_argument(smi.Argument("entity_endpoints", title="Entity Endpoints",
        #                                  description="",
        #                                  required_on_create=True,
        #                                  required_on_edit=False))
        scheme.add_argument(smi.Argument("ssl_certificate_verification", title="SSL Certificate Verification",
                                         description="",
                                         required_on_create=False,
                                         required_on_edit=False))
        return scheme

    def get_app_name(self):
        return "Splunk_TA_Dynatrace"

    def validate_input(helper, definition):
        pass

    def collect_events(helper, ew):
        dynatrace_account_input = helper.get_arg("dynatrace_account")
        dynatrace_tenant_input = dynatrace_account_input["username"]


        if dynatrace_tenant_input.find('https://') == 0:
            opt_dynatrace_tenant = dynatrace_tenant_input
        elif dynatrace_tenant_input.find('http://') == 0:
            opt_dynatrace_tenant = dynatrace_tenant_input.replace('http://', 'https://')
        else:
            opt_dynatrace_tenant = 'https://' + dynatrace_tenant_input

        opt_dynatrace_api_token = dynatrace_account_input["password"]
        endpoint = helper.get_arg("dynatrace_apiv2_endpoint")
        opt_dynatrace_collection_interval_minutes = int(helper.get_arg("dynatrace_collection_interval"))
        opt_ssl_certificate_verification = helper.get_arg('ssl_certificate_verification')
        index = helper.get_arg("index")

        time_range = util.get_from_time(int(opt_dynatrace_collection_interval_minutes))

        # Set a default list of entity types for the 'entities' endpoint
        default_entity_types = ['HOST', 'PROCESS_GROUP_INSTANCE', 'PROCESS_GROUP', 'APPLICATION', 'SERVICE']

        sourcetype_mapping = {
            "problems": "dynatrace:problems",
            "events": "dynatrace:events",
            "entities": "dynatrace:entities",
            "synthetic_locations": "dynatrace:synthetic_locations",
            # Add more mappings as needed
        }
        sourcetype = sourcetype_mapping.get(endpoint, None)

        if endpoint == 'entities':
            entity_types = default_entity_types
        else:
            entity_types = None

        requests_info = util.prepare_dynatrace_request(
            endpoint,
            opt_dynatrace_tenant,
            opt_dynatrace_api_token,
            time=time_range,
            entity_types=entity_types
        )

        dynatrace_data = util.get_dynatrace_data(requests_info, verify=opt_ssl_certificate_verification,
                                                 opt_helper=helper)

        helper.log_debug('dynatrace_tenant: {}'.format(opt_dynatrace_tenant))
        helper.log_debug('dynatrace_collection_interval: {}'.format(opt_dynatrace_collection_interval_minutes))

        for record in dynatrace_data:
            eventLastSeenTime = None
            if "lastSeenTimestamp" in record:
                eventLastSeenTime = record["lastSeenTimestamp"] / 1000
                record.update({"timestamp": eventLastSeenTime})
            record['endpoint'] = endpoint
            serialized = json.dumps(record, sort_keys=True)
            event = helper.new_event(data=serialized, time=eventLastSeenTime, host=None, index=index, source=None,
                                     sourcetype=sourcetype, done=True, unbroken=True)
            ew.write_event(event)

    def get_account_fields(self):
        account_fields = []
        account_fields.append("dynatrace_account")
        return account_fields

    def get_checkbox_fields(self):
        checkbox_fields = []
        checkbox_fields.append("ssl_certificate_verification")
        return checkbox_fields

    def get_global_checkbox_fields(self):
        if self.global_checkbox_fields is None:
            checkbox_name_file = os.path.join(bin_dir, 'global_checkbox_param.json')
            try:
                if os.path.isfile(checkbox_name_file):
                    with open(checkbox_name_file, 'r') as fp:
                        self.global_checkbox_fields = json.load(fp)
                else:
                    self.global_checkbox_fields = []
            except Exception as e:
                self.log_error('Get exception when loading global checkbox parameter names. ' + str(e))
                self.global_checkbox_fields = []
        return self.global_checkbox_fields

if __name__ == "__main__":
    exitcode = ModInputdynatrace_api_v2().run(sys.argv)
    sys.exit(exitcode)