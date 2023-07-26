import pathlib
from unittest import mock
import re
import os
from requests.models import Response, PreparedRequest
import package.bin.util as util
import unittest
from dynatrace_types import CollectionInterval, MetricDescriptor, MetricId, MetricSelector, MetricDescriptorCollection, Tenant
from package.bin.util import V2Endpoints
import pickle
import json
from pygments import highlight
from pygments.lexers import JsonLexer, find_lexer_class_by_name
from pygments.formatters import TerminalFormatter
from colorama import init
from datetime import datetime, timedelta
from urllib import parse
from urllib3.util import Url


import package.bin.metrics_util as dt_metrics
from pathlib import Path
import pickle_test_inputs
from pprint import pprint

def request_info_generator():
    """Generate request info for util.prepare_dynatrace_request()"""
    time = util.get_from_time()
    tenant = "test_tenant"
    api_token = "test_token"

    for enum in V2Endpoints:
        endpoint = enum
        # Expected url after formatting
        params = {}
        expected_url = tenant + endpoint.url
        entity_types = ["HOST", "SERVICE", "APPLICATION", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE", "SYNTHETIC_TEST","SYNTHETIC_TEST_STEP"]

        if endpoint.url_param_map:
            params = {endpoint.url_param_map: "Computer1234"}
            expected_url = expected_url.format(id=params[endpoint.url_param_map])

        yield endpoint, tenant, api_token, time, params, entity_types, expected_url


def pickle_paths():
    """Location of pickled test inputs"""
    # Calculate the absolute path of the directory containing the pickle files
    # This assumes that the pickle directory is in the same directory as the current script
    pickle_dir = Path(pickle_test_inputs.__path__[0])
    for file_path in pickle_dir.glob("*.pkl"):
        yield file_path


def parse_pickled_test_inputs(file_path):
    """Parse pickled test input
    Example file name:
    20230725120417070411_https%3A%2F%2Fjlw10381.live.dynatrace.com%2Fapi%2Fv2%2Fentities_response.pkl"""
    unquoted = parse.unquote(file_path.name)
    split = unquoted.split('_')
    timestamp = datetime.strptime(split[0], "%Y%m%d%H%M%S%f")
    url = split[1]
    file_type_ext = "_".join(split[2:])
    file_type = os.path.splitext(file_type_ext)[0]

    return file_path.name, file_type, timestamp, url


def pickled_test_inputs():
    """Load pickled test inputs"""
    for file_path in pickle_paths():
        with open(file_path, "rb") as f:
            file_name, file_type, timestamp, url = parse_pickled_test_inputs(file_path)
            yield file_name, file_type, timestamp, url, pickle.load(f)


def get_endpoint_info(url):
    """Match a URL to an EndpointInfo object."""
    for endpoint in V2Endpoints:
        endpoint_url_regex = re.escape(endpoint.value.url).replace(r"\{id\}", r"[^/]+")
        # Ensure endpoint.url is at the end of url
        endpoint_url_regex = r".*{}$".format(endpoint_url_regex)
        if re.search(endpoint_url_regex, url):
            return endpoint
    return None


def manual_pickle_review():
    for file_name, file_type, timestamp, url, data in sorted(pickled_test_inputs()):
        print(f"file_name: {file_name}")
        print(f"file_type: {file_type}")
        print(f"timestamp: {timestamp}")
        print(f"url: {url}")

        if file_type == 'response':
            try:
                json_content = json.loads(data.text)
                print(highlight(json.dumps(json_content), JsonLexer(), TerminalFormatter()))
            except json.JSONDecodeError:
                print('Data was not JSON')

            print(f'Status code: {data.status_code}')
            print(f'Headers: {highlight(json.dumps(dict(data.headers)), JsonLexer(), TerminalFormatter())}')

        elif file_type == 'inputs':
            # convert the tuple to a dictionary
            input_dict = {'url': data[0], 'headers': data[1], 'params': data[2], 'selector': data[3]}
            print(f'data: {highlight(json.dumps(input_dict), JsonLexer(), TerminalFormatter())}')

        else:
            if isinstance(data, dict):
                print(f'data: {highlight(json.dumps(data), JsonLexer(), TerminalFormatter())}')
            elif isinstance(data, PreparedRequest):
                print(f'Method: {data.method}')
                print(f'URL: {data.url}')
                print(f'Headers: {highlight(json.dumps(dict(data.headers)), JsonLexer(), TerminalFormatter())}')
                print(f'Body: {data.body}')

        user_input = input("Press enter to continue, or 'q' to quit: ")
        if user_input.lower() == 'q':
            break
        print()


class TestUtil(unittest.TestCase):
    def setUp(self):
        # define your setup variables here if needed
        pass

    def test_format_url_and_pop_params(self):
        endpoint = V2Endpoints.ENTITY
        url = "https://example.com/api/v2/{id}"
        params = {"entity_id": "1234", "name": "test"}

        # Expected values
        expected_url = "https://example.com/api/v2/1234"
        expected_params = {"name": "test"}

        result_url, result_params = util.format_url_and_pop_params(endpoint, params, url)
        print()
        print(f"result_url: {result_url}")
        print(f"result_params: {result_params}")

        self.assertEqual(result_url, expected_url)
        self.assertEqual(result_params, expected_params)


    def test_prepare_dynatrace_request(self):
        time = util.get_from_time()
        tenant = "test_tenant"
        api_token = "test_token"

        for endpoint, tenant, api_token, time, params, entity_types, expected_url in request_info_generator():
            result = util.prepare_dynatrace_request(endpoint, tenant, api_token, time=time, params=params,
                                                    entity_types=entity_types)

            print()
            print(f"time: {time}")
            print(f"expected_url: {expected_url}")
            print(f"result: {result}")

            self.assertEqual(result[0][0], expected_url)

    def test_parse_dynatrace_response(self):
        file_paths = sorted(pickled_test_inputs())
        for file_name, file_type, timestamp, url, data in file_paths:
            endpoint = get_endpoint_info(url)
            print()
            print(f"file_name: {file_name}")
            if file_type == "response":
                response = data.json()
                result = util.parse_dynatrace_response(response, endpoint)
                print()
                print(f"file_type: {file_type}")
                print(f"timestamp: {timestamp}")
                print(f"url: {url}")
                print(f"result: {result}")
            assert True

    def test_get_dynatrace_data(self):
        for endpoint, tenant, api_token, time, params, entity_types, expected_url in request_info_generator():
            requests_info = util.prepare_dynatrace_request(endpoint, tenant, api_token, time=time, params=params,
                                                           entity_types=entity_types)

            print()
            print(f"requests_info: {requests_info}")
            for url, headers, params, endpoint in requests_info:
                print()
                print(f"url: {url}")
                print(f"headers: {headers}")
                print(f"params: {params}")
                print(f"endpoint: {endpoint}")


            # Create a mock response
            mock_response = Response()
            mock_response.status_code = 200
            mock_response._content = b'{"key": "value"}'  # Set the content to be some JSON

            # Create a mock session
            mock_session = mock.Mock()
            mock_session.send.return_value = mock_response
            mock_session.merge_environment_settings.return_value = {}

            # Now when get_dynatrace_data calls session.get, it will get the mock response
            result = util.get_dynatrace_data(mock_session, requests_info)
            print(f"result: {result}")

            # You can now assert that the result is what you expect
            self.assertEqual(result, result)  # replace ... with the expected result


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

class TestMetricsUtil(unittest.TestCase):
    def test_parse_metric_selectors(self):
        print()
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
        print()
        path_from_package = Path('package/tests/pickle_requests')
        script_location = pathlib.Path(__file__).resolve()

        # Calculate the absolute path of the directory containing the pickle files
        # This assumes that the pickle directory is in the same directory as the current script
        pickle_path = script_location.parent / "pickle_requests"
        prefix = "response_https__fbk23429livedynatracecom_api_v2_"
        file_name = "metrics_1687888114.pkl"

        metrics_request = pickle.load(open(Path(pickle_path, prefix + file_name), 'rb'))
        metrics_response = pickle.load(open(Path(pickle_path, prefix + file_name), 'rb'))
        metrics_response: MetricDescriptorCollection = pickle.load(open(Path(pickle_path, prefix + file_name), 'rb'))

        # Metric descriptor returned from call to /api/v2/metrics/{metricKey}
        metric_descriptor_request = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"), 'rb'))
        metric_descriptor_response = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"), 'rb'))

        metrics_query_request = pickle.load(open(Path(pickle_path, prefix + "metrics_query_1687888114.pkl"), 'rb'))
        metrics_query_response = pickle.load(open(Path(pickle_path, prefix + "metrics_query_1687888114.pkl"), 'rb'))

        # Parse metrics response
        pprint(util.parse_dynatrace_response(metrics_response, V2Endpoints.METRICS))

        metric_id = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"), 'rb'))
        pprint(util.parse_dynatrace_response(metric_id, V2Endpoints.METRICS_QUERY))

        raw_metrics = pickle.load(open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_query_1687888114.pkl"), 'rb'))

    def test_process_timeseries_data(self):
        # TODO: Fix this test
        for file_name, file_type, timestamp, url, data in sorted(pickled_test_inputs()):
            endpoint = get_endpoint_info(url)
            if endpoint == V2Endpoints.METRICS_QUERY and file_type == "response":
                print()
                print(f'file_name: {file_name}')
                print(f'file_type: {file_type}')
                print(f'timestamp: {timestamp}')
                print(f'url: {url}')
                parsed_data = util.parse_dynatrace_response(data.json(), endpoint)
                print()
                print(f'parsed_data: {parsed_data}')
                process_timeseries_data = [item for item in dt_metrics.flatten_and_zip_timeseries(parsed_data)]
                for data_point in process_timeseries_data:
                    print(f'data_point: {data_point}')

            assert True

    def test_build_event_data(self):
        metric_descriptor: MetricDescriptor
        opt_dynatrace_tenant: Tenant
        metric_id: MetricId
        metric_selector: MetricSelector

        for file_name, file_type, timestamp, url, data in sorted(pickled_test_inputs()):
            endpoint = get_endpoint_info(url)
            if endpoint == V2Endpoints.METRIC_DESCRIPTORS and file_type == "response":
                metric_descriptor = util.parse_dynatrace_response(data.json(), endpoint)
                print(f'metric_descriptor: {metric_descriptor}')
                metric_id = metric_descriptor['metricId']
                #TODO: Find metric_selector

            if endpoint == V2Endpoints.METRICS_QUERY and file_type == "response":
                print()
                print(f'file_name: {file_name}')
                print(f'file_type: {file_type}')
                print(f'timestamp: {timestamp}')
                print(f'url: {url}')
                parsed_data = util.parse_dynatrace_response(data.json(), endpoint)
                print()
                print(f'parsed_data: {parsed_data}')
                process_timeseries_data = [item for item in dt_metrics.flatten_and_zip_timeseries(parsed_data)]
                for data_point in process_timeseries_data:
                    print(f'data_point: {data_point}')
                    event_data = dt_metrics.build_event_data(data_point, metric_descriptor, "opt_dynatrace_tenant")
                    print(f'event_data: {event_data}')

            assert True


if __name__ == '__main__':
    unittest.main()
