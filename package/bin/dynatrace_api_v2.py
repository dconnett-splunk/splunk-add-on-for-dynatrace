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
from splunktaucclib.modinput_wrapper import base_modinput as base_mi
import requests
import util
from util import Endpoint
from pathlib import Path
from dynatrace_types_37 import *



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

        scheme.add_argument(smi.Argument("dynatrace_apiv2_endpoint", title="Dynatrace API Endpoint",
                                         description="Dynatrace API endpoint to be used for data collection.",
                                         required_on_create=True,
                                         required_on_edit=False))

        # scheme.add_argument(smi.Argument("entity_endpoints", title="Entity Endpoints",
        #                                  description="",
        #                                  required_on_create=True,
        #                                  required_on_edit=False))

        return scheme

    def get_app_name(self):
        return "Splunk_TA_Dynatrace"

    def validate_input(helper, definition):
        pass

    def collect_events(helper, ew):
        dynatrace_account_input = helper.get_arg("dynatrace_account")
        dynatrace_tenant_input = dynatrace_account_input["username"]
        opt_dynatrace_tenant: Tenant = util.parse_url(dynatrace_tenant_input)
        opt_dynatrace_api_token: APIToken = dynatrace_account_input["password"]

        endpoint_string = helper.get_arg("dynatrace_apiv2_endpoint")
        if ',' in endpoint_string:
            endpoint = tuple(Endpoint.get_endpoint(val.strip()) for val in endpoint_string.split(","))
            helper.log_info(f'endpoint: {endpoint}')
        else:
            endpoint: Endpoint = Endpoint.get_endpoint(endpoint_string)

        opt_dynatrace_collection_interval_minutes: CollectionInterval = CollectionInterval(int(helper.get_arg("dynatrace_collection_interval")))
        # opt_ssl_certificate_verification = helper.get_arg('ssl_certificate_verification')
        opt_ssl_certificate_verification = util.get_ssl_certificate_verification(helper)
        index = helper.get_arg("index")

        time_start = util.get_from_time(opt_dynatrace_collection_interval_minutes)

        # Set a default list of entity types for the 'entities' endpoint
        # TODO - Need to make this configurable
        default_entity_types = ["HOST", "PROCESS_GROUP_INSTANCE", "PROCESS_GROUP", "APPLICATION", "SERVICE", "SYNTHETIC_TEST", "SYNTHETIC_TEST_STEP"]

        # TODO - Change synthetic_tests_on_demand to synthetic_executions_on_demand
        # Will also need to change strings in the apiv2.py file and the util.py selectors and enpoints
        sourcetype_mapping = {
            Endpoint.ENTITIES: "dynatrace:entities",
            (Endpoint.ENTITIES, Endpoint.ENTITY): "dynatrace:entities",
            Endpoint.EVENTS: "dynatrace:events",
            Endpoint.PROBLEMS: "dynatrace:problems",
            (Endpoint.PROBLEMS, Endpoint.PROBLEM): "dynatrace:problem_details",
            Endpoint.SYNTHETIC_LOCATIONS: "dynatrace:synthetic_locations",
            Endpoint.SYNTHETIC_MONITORS_HTTP: "dynatrace:synthetic_monitors",
            Endpoint.SYNTHETIC_TESTS_ON_DEMAND: "dynatrace:on_demand_executions",
            (Endpoint.SYNTHETIC_MONITORS_HTTP, Endpoint.SYNTHETIC_MONITOR_HTTP): "dynatrace:synthetic_monitor_details"
        }

        keys_to_remove = ['responseBody', 'peerCertificateDetails']
        sourcetype = sourcetype_mapping.get(endpoint, None)

        params = {'time': time_start}
        dynatrace_data = util.execute_session(endpoint, opt_dynatrace_tenant, opt_dynatrace_api_token, params, opt_helper=helper)

        helper.log_debug('dynatrace_tenant: {}'.format(opt_dynatrace_tenant))
        helper.log_debug('dynatrace_collection_interval: {}'.format(opt_dynatrace_collection_interval_minutes))

        if dynatrace_data:
            for record in dynatrace_data:
                helper.log_debug('record: {}'.format(record))
                serialized = json.dumps(record, sort_keys=True)
                event = helper.new_event(data=serialized, host=None, index=index, source=None,
                                         sourcetype=sourcetype, done=True, unbroken=True)
                ew.write_event(event)
        else:
            helper.log_warning(f'No data returned from Dynatrace API for endpoint: {endpoint}')

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
