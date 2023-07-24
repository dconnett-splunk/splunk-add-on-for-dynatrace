import pathlib
from wsgiref import util

import package.bin.metrics_util as dt_metrics
import package.bin.util as util
from unittest import TestCase
from pprint import pprint
import json
from pathlib import Path
import pickle
import util
import re
from dynatrace_types import *
from datetime import datetime, timedelta

metric_selector = 'builtin:host.cpu.usage:merge(0):avg'
metric_selectors_from_file = """builtin:host.cpu.usage:max
builtin:host.cpu.usage:fold(max),builtin:host.cpu.usage:splitBy()
builtin:kubernetes.pods
  :filter(eq("k8s.cluster.name","preproduction"))
  :splitBy("dt.entity.cloud_application")
  :max"""

metric_selector_list = ['builtin:host.cpu.usage:max',
                        'builtin:host.cpu.usage:fold(max)',
                        'builtin:host.cpu.usage:splitBy()',
                        'builtin:kubernetes.pods:filter(eq("k8s.cluster.name","preproduction")):splitBy("dt.entity.cloud_application"):max']

metric_selector_file_path = 'metric_selectors.txt'


class TestMetricsUtil(TestCase):
    def test_parse_metric_selectors(self):
        metric_selector_file: Path = Path(metric_selector_file_path)
        parsed_metric_selectors = dt_metrics.parse_metric_selectors_from_file(metric_selector_file)
        for parsed, expected in zip(parsed_metric_selectors, metric_selector_list):
            print(f'parsed: {parsed}, expected: {expected}')
            self.assertEqual(expected, parsed)

        # Convert list into JSON formatted string for better readability
        print(f'parsed_metric_selectors:\n{json.dumps(parsed_metric_selectors, indent=4)}')

        parsed_metric_selectors_from_file = dt_metrics.parse_metric_selectors_from_file(metric_selector_file)
        print(f'parsed_metric_selectors_from_file:\n{json.dumps(parsed_metric_selectors_from_file, indent=4)}')

    def test_parse_metric_selectors_text_area(self):
        parsed_metric_selectors_text_area = dt_metrics.parse_metric_selectors_text_area(metric_selectors_from_file)
        self.assertEqual(['builtin:host.cpu.usage:merge(0):avg'], dt_metrics.parse_metric_selectors_text_area(metric_selector))
        print()
        parsed_metric_selectors_text_area = dt_metrics.parse_metric_selectors_text_area(metric_selector)
        # Use json.dumps for pretty-printing
        print(f'parse_metric_selectors_text_area:\n{json.dumps(parsed_metric_selectors_text_area, indent=4)}')

    def test_time(self):
        # Used in MetricsV2
        opt_dynatrace_collection_interval_minutes: CollectionInterval = CollectionInterval(5)
        end_time = f"{datetime.now().isoformat()}Z"
        start_time = f"{(datetime.now() - timedelta(minutes=opt_dynatrace_collection_interval_minutes)).isoformat()}Z"

        print()
        print(f'collection_interval_minutes: {opt_dynatrace_collection_interval_minutes}')
        print(f'end_time: {end_time}')
        print(f'start_time: {start_time}')

        # Centralized version
        from_time = util.get_from_time(opt_dynatrace_collection_interval_minutes)
        from_time_utc = util.get_from_time_utc(opt_dynatrace_collection_interval_minutes)
        start_timestamp = util.calculate_utc_start_timestamp(opt_dynatrace_collection_interval_minutes)
        deftault_time = util.default_time()
        print(f'from_time: {from_time}')
        print(f'from_time_utc: {from_time_utc}')
        print(f'start_timestamp: {start_timestamp}')
        print(f'deftault_time: {deftault_time}')

    def test_metric_request(self):
        path_from_package = Path('package/tests/pickle_requests')
        pickle_path = Path('pickle_requests')
        prefix = "response_https__fbk23429livedynatracecom_api_v2_"
        file_name = "metrics_1687888114.pkl"


        # Call to /api/v2/metrics
        # Returns

        metrics_request = pickle.load(open(Path(pickle_path, prefix + file_name), 'rb'))
        metrics_response = pickle.load(open(Path(pickle_path, prefix + file_name), 'rb'))
        metrics_response: MetricDescriptorCollection = pickle.load(open(Path(pickle_path, prefix + file_name), 'rb'))

        # Metric descriptor returned from call to /api/v2/metrics/{metricKey}
        metric_descriptor_request = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"), 'rb'))
        metric_descriptor_response = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"), 'rb'))

        metrics_query_request = pickle.load(open(Path(pickle_path, prefix + "metrics_query_1687888114.pkl"), 'rb'))
        metrics_query_response = pickle.load(open(Path(pickle_path, prefix + "metrics_query_1687888114.pkl"), 'rb'))

        # Parse metrics response
        pprint(util.parse_dynatrace_response(metrics_response, 'metrics'))

        metric_id = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"), 'rb'))
        pprint(util.parse_dynatrace_response(metric_id, 'metric_descriptors'))

        raw_metrics = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_query_1687888114.pkl"), 'rb'))
