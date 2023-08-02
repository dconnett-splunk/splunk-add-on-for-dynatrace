import json
import os
import pickle
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint
from unittest.mock import patch
from urllib import parse

import requests
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer
from requests.models import Response, PreparedRequest, Request

import package.bin.metrics_util as dt_metrics
import package.bin.util as util
import pickle_test_inputs
from dynatrace_types import *
from package.bin.util import Endpoint

version = '2.0.8'
script_location: Path = Path(__file__).resolve()


def parse_open_api_spec(oas_spec: Path):
    """Parse an OpenAPI specification file"""
    with open(oas_spec, 'r') as f:
        spec = json.load(f)
    return spec


def get_example_from_spec(spec, path, method='get', response_code='200'):
    """Get example from the OpenAPI spec for a certain path, method and response code"""
    try:
        response_content_type = list(
            spec.get('paths', {}).get(path, {}).get(method, {}).get('responses', {}).get(response_code, {}).get(
                'content', {}))[0]
        schema_ref = spec.get('paths', {}).get(path, {}).get(method, {}).get('responses', {}).get(response_code,
                                                                                                  {}).get('content',
                                                                                                          {}).get(
            response_content_type, {}).get('schema', {}).get('$ref', '')
        schema_name = schema_ref.split('/')[-1]
        return spec.get('components', {}).get('schemas', {}).get(schema_name, {}).get('example', None)
    except IndexError:
        return None


def request_info_generator():
    """Generate request info for util.prepare_dynatrace_request()"""
    print('request_info_generator() called')
    time = util.get_from_time()
    tenant = "http://localhost:12345"
    api_token = "test_token"

    for enum in Endpoint:
        endpoint = enum
        # Expected url after formatting
        params = {}
        expected_url = tenant + endpoint.url
        print(f'request_info_generator() endpoint: {endpoint}')
        print(f'request_info_generator() expected_url: {expected_url}')
        print(f'request_info_generator() endpoint.url_path_param: {endpoint.url_path_param}')
        extra_params = ["HOST", "SERVICE", "APPLICATION", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE", "SYNTHETIC_TEST",
                        "SYNTHETIC_TEST_STEP"]

        if endpoint.url_path_param:
            params = Params({endpoint.url_path_param: "Computer1234"})
            print(f'request_info_generator() params: {params}')
            expected_url, new_params = util.format_url_and_pop_path_params(endpoint, params, expected_url)

        yield endpoint, tenant, api_token, time, params, extra_params, expected_url


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
    for endpoint in Endpoint:
        endpoint_url_regex = re.escape(endpoint.value.url)
        # Replace all strings enclosed in {} with a regex that matches any characters excluding the /
        endpoint_url_regex = re.sub(r'\\{.*?\\}', r"[^/]+", endpoint_url_regex)
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
        self.spec = parse_open_api_spec(Path('dynatrace_oas_spec3.json'))

    def test_format_url_and_pop_params(self):
        endpoint = Endpoint.ENTITY
        url = URL("https://example.com/api/v2/{entityId}")
        params = Params({"entityId": "1234", "name": "test"})

        # Expected values
        expected_url = "https://example.com/api/v2/1234"
        expected_params = {"name": "test"}

        result_url, result_params = util.format_url_and_pop_path_params(endpoint, params, url)
        print()
        print(f"result_url: {result_url}")
        print(f"result_params: {result_params}")

        self.assertEqual(expected_url, result_url)
        self.assertEqual(expected_params, result_params)

    @staticmethod
    def generate_dynatrace_params():
        time = util.get_from_time()

        api_token = "test_token"
        print()
        print('generate_dynatrace_params() called')

        for endpoint_outer, tenant, api_token, time, params, extra_params, expected_url in request_info_generator():
            print()
            print('=' * 100)
            print('New request_info_generator() iteration')
            print(f'endpoint: {endpoint_outer}')
            tenant = "http://localhost:12345"
            print(f'tenant: {tenant}')
            print(f'api_token: {api_token}')
            print(f'time: {time}')
            print(f'generated params: {params}')
            print(f'extra_params: {extra_params}')

            result = util.prepare_dynatrace_params(base_url=tenant, params=params, endpoint=endpoint_outer,
                                                   extra_params=extra_params)
            print(f'generate_dynatrace_params() result: {result}')
            for url, prepared_params, endpoint in result:
                print('-' * 100)
                print(f"inner url: {url}")
                print(f"prepared params: {prepared_params}")
                print(f"endpoint: {endpoint}")
                print()
                print(f"time: {time}")
                print(f"expected_url: {expected_url}")

                yield expected_url, url, prepared_params, endpoint

    def test_prepare_dynatrace_params(self):
        print()
        print('test_prepare_dynatrace_params() called')
        for expected_url, url, prepared_params, endpoint in self.generate_dynatrace_params():
            print(f'expected_url: {expected_url}')
            print(f'prepared_params: {prepared_params}')
            print(f'url: {url}')
            self.assertEqual(expected_url, url)

    def test_prepare_dynatrace_request(self):
        for endpoint, tenant, api_token, time, params, extra_params, expected_url in request_info_generator():
            print()
            print('=' * 100)
            prepared_params = util.prepare_dynatrace_params(base_url=tenant, params=params, endpoint=endpoint,
                                                            extra_params=extra_params)
            for url, prepared_params, endpoint in prepared_params:
                print('-' * 100)
                headers = util.prepare_dynatrace_headers(api_token)
                request: Request = requests.Request('GET', url, headers=headers, params=prepared_params)
                with requests.Session() as session:
                    prepared_request = util.prepare_dynatrace_request(session, url, prepared_params)
                    print(f'url: {prepared_request.url}')
                    print(f'headers: {prepared_request.headers}')
                    print(f'body: {prepared_request.body}')
                    if session.params:
                        print(f'params: {session.params}')

                    settings = session.merge_environment_settings(prepared_request.url, {}, None, None, None)

                    print(f"prepared_request: {prepared_request}")

                    # Create a mock response
                    mock_response = Response()
                    mock_response.status_code = 200
                    mock_response._content = b'{"key": "value"}'

    def test_parse_dynatrace_response(self):
        file_paths = sorted(pickled_test_inputs())
        for file_name, file_type, timestamp, url, data in file_paths:
            if get_endpoint_info(url):
                endpoint = get_endpoint_info(url)
            print()
            print(f"file_name: {file_name}")
            if file_type == "response":
                response = data.json()
                print(f"response: {response}")
                print(f"endpoint: {endpoint}")
                result = util.parse_dynatrace_response(response, endpoint)
                print()
                print(f"file_type: {file_type}")
                print(f"timestamp: {timestamp}")
                print(f"url: {url}")
                print(f"result: {result}")
            assert True

    @patch('requests.Session', autospec=True)
    def test_get_dynatrace_data(self, mock_session):
        for endpoint, tenant, api_token, time, params, extra_params, expected_url in request_info_generator():
            print()
            print('=====================================')
            print('New request_info_generator() iteration')
            print(f'endpoint: {endpoint}')
            tenant = "http://localhost:12345"
            print(f'tenant: {tenant}')
            print(f'api_token: {api_token}')
            print(f'time: {time}')
            print(f'params: {params}')
            print(f'extra_params: {extra_params}')
            print(f'expected_url: {expected_url}')
            params = {'time': time}
            prepared_params_list = util.prepare_dynatrace_params(tenant, params, endpoint, extra_params)

            prepared_headers = util.prepare_dynatrace_headers(api_token)
            with requests.Session() as session:
                session.headers.update(prepared_headers)
                print()
                print(f"headers: {prepared_headers}")
                print(f"params: {params}")
                print(f"endpoint: {endpoint}")
                result = util.get_dynatrace_data(session, prepared_params_list)

                print(f"result: {result}")

                stripped_url = endpoint.url.replace("/api/v2", "", 1)
                print(f'endpoint url: {stripped_url}')
                expected_result = get_example_from_spec(self.spec, stripped_url)
                self.assertEqual(expected_result, expected_result)

    def test_merge_endpoint_params_synthetic(self):
        print()
        endpoint = Endpoint.SYNTHETIC_TESTS_ON_DEMAND
        time = str(util.get_from_time_utc())
        params = Params({'time': time})
        expected_params = {'schedulingFrom': time}
        result = util.format_params(endpoint, params)
        print()
        print(f'result: {result}')
        self.assertEqual(expected_params, result)

    def test_merge_endpoint_params_metrics(self):
        print()
        endpoint = Endpoint.METRICS
        time = str(util.get_from_time_utc())
        params = Params({'time': time, 'pageSize': '10', 'metricKey': 'builtin:host.cpu.usage:merge(0):avg'})
        expected_params = {'fields': 'unit,aggregationTypes', 'writtenSince': time, 'pageSize': '10',
                           'metricKey': 'builtin:host.cpu.usage:merge(0):avg'}
        result = util.format_params(endpoint, params)
        print(f'result: {result}')
        self.assertEqual(expected_params, result)

    def test_merge_endpoint_params_entities(self):
        print()
        extra_params = ["HOST", "SERVICE", "APPLICATION", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE", "SYNTHETIC_TEST",
                        "SYNTHETIC_TEST_STEP"]
        time = str(util.get_from_time_utc())
        endpoint = Endpoint.ENTITIES
        params = Params({'time': time, 'pageSize': '10', 'entitySelector': 'HOST'})
        expected_params = {'time': time, 'pageSize': '10', 'entitySelector': 'type(\"HOST\")'}
        result = util.format_params(endpoint, params)
        print(f'result: {result}')
        self.assertEqual(expected_params, result)

    def test_build_url(self):
        print()
        endpoint = Endpoint.METRIC_DESCRIPTORS
        tenant = Tenant("https://fbk23429.live.dynatrace.com")
        params = Params({'metricKey': 'builtin:host.cpu.usage:merge(0):avg'})
        print(f'params: {params}')
        expected_url = 'https://fbk23429.live.dynatrace.com/api/v2/metrics/builtin:host.cpu.usage:merge(0):avg'
        result = util.build_url(endpoint, tenant, params)
        print(f'result: {result}')
        self.assertEqual(expected_url, result)

    # def test_join_data_live(self):
    #     print()
    #     endpoint = Endpoints.ENTITIES
    #     secrets = util.parse_secrets_env()
    #     tenant = secrets['dynatrace_tenant']
    #     api_token = secrets['dynatrace_api_token']
    #     params = Params({'time': util.get_from_time()})
    #     extra_params = ["HOST", "SERVICE", "APPLICATION", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE", "SYNTHETIC_TEST",
    #                     "SYNTHETIC_TEST_STEP"]
    #
    #     prepared_params_list = util.prepare_dynatrace_params(tenant, params, endpoint, extra_params)
    #     prepared_headers = util.prepare_dynatrace_headers(api_token)
    #
    #     # Entities
    #     #TODO Refactor this to use execute_session.
    #     print('Test entities')
    #     with requests.Session() as session:
    #         session.headers.update(prepared_headers)
    #         print()
    #         print(f"headers: {prepared_headers}")
    #         print(f"params: {params}")
    #         print(f"endpoint: {endpoint}")
    #         result: EntitiesList = util.get_dynatrace_data(session, prepared_params_list)
    #         for entity in result:
    #             print(f'entity: {entity}')
    #             entity_id = entity['entityId']
    #             params = Params({'time': util.get_from_time(),
    #                              'entityId': entity_id})
    #             extra_params = ["HOST", "SERVICE", "APPLICATION", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE",
    #                             "SYNTHETIC_TEST", "SYNTHETIC_TEST_STEP"]
    #             endpoint = Endpoints.ENTITY
    #             prepared_params_list = util.prepare_dynatrace_params(tenant, params, endpoint, extra_params)
    #             result2 = util.get_dynatrace_data(session, prepared_params_list)
    #             print(f'result2: {result2}')
    #
    #     with requests.Session() as session:
    #         session.headers.update(prepared_headers)
    #         # Problems
    #         print('Test problems')
    #         collection_interval = str(util.get_from_time())
    #         endpoint2 = Endpoints.PROBLEMS
    #         params2: Params = Params({'time': collection_interval})
    #         prepared_params_list2 = util.prepare_dynatrace_params(tenant, params2, endpoint2)
    #         result3 = util.get_dynatrace_data(session, prepared_params_list2)
    #         print(f'result3: {result3}')
    #
    #         for problem in result3:
    #             problem_id = problem['problemId']
    #             endpoint3 = Endpoints.PROBLEM
    #             params3 = Params({'time': util.get_from_time(40400),
    #                               'problemId': problem_id})
    #             prepared_params_list3 = util.prepare_dynatrace_params(tenant, params3, endpoint3)
    #             result4 = util.get_dynatrace_data(session, prepared_params_list3)
    #             print(f'result4: {result4}')
    #
    #             self.assertEqual(result, result)

    def test_execute_session_entities(self):
        print()
        endpoint = [Endpoint.ENTITIES, Endpoint.ENTITY]
        secrets = util.parse_secrets_env()
        tenant = secrets['dynatrace_tenant']
        api_token = secrets['dynatrace_api_token']
        params = Params({'time': util.get_from_time()})
        extra_params = ["HOST", "SERVICE", "APPLICATION", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE",
                        "SYNTHETIC_TEST",
                        "SYNTHETIC_TEST_STEP"]

        result = util.execute_session(endpoint, tenant, api_token, params, extra_params)
        for entity in result:
            print(f'entity: {entity}')



    def test_execute_session_problems(self):
        print()
        endpoint = Endpoint.PROBLEMS
        secrets = util.parse_secrets_env()
        tenant = secrets['dynatrace_tenant']
        api_token = secrets['dynatrace_api_token']
        params = Params({'time': util.get_from_time()})

        result = util.execute_session(endpoint, tenant, api_token, params)
        for problem in result:
            print(f'problem: {problem}')

    def test_execute_session_synthetic(self):
        print()
        endpoint = [Endpoint.SYNTHETIC_MONITORS_HTTP, Endpoint.SYNTHETIC_MONITOR_HTTP]
        secrets = util.parse_secrets_env()
        tenant = secrets['dynatrace_tenant']
        api_token = secrets['dynatrace_api_token']
        params = Params({'time': util.get_from_time()})

        result = util.execute_session(endpoint, tenant, api_token, params)
        for synthetic in result:
            print(f'synthetic: {synthetic}')


    def test_execute_session_syntheticv2(self):
        print()
        endpoint = Endpoint.SYNTHETIC_MONITORS_HTTP_V2
        secrets = util.parse_secrets_env()
        tenant = secrets['dynatrace_tenant']
        api_token = secrets['dynatrace_api_token']
        params = Params({'time': util.get_from_time()})

        result = util.execute_session(endpoint, tenant, api_token, params)
        for synthetic in result:
            print(f'synthetic: {synthetic}')

    def test_synthetic_locations(self):
        print()
        endpoint = Endpoint.SYNTHETIC_LOCATIONS
        secrets = util.parse_secrets_env()
        tenant = secrets['dynatrace_tenant']
        api_token = secrets['dynatrace_api_token']
        params = Params({'time': util.get_from_time()})

        result = util.execute_session(endpoint, tenant, api_token, params)
        for synthetic in result:
            print(f'synthetic: {synthetic}')

    def test_events(self):
        print()
        endpoint = Endpoint.EVENTS
        secrets = util.parse_secrets_env()
        tenant = secrets['dynatrace_tenant']
        api_token = secrets['dynatrace_api_token']
        params = Params({'time': util.get_from_time()})

        result = util.execute_session(endpoint, tenant, api_token, params)
        for event in result:
            print(f'event: {event}')


metric_selector = 'builtin:host.cpu.usage:merge(0):avg'
metric_selectors_from_file = """builtin:host.cpu.usage:max
builtin:host.cpu.usage:fold(max)
builtin:host.cpu.usage:splitBy()
builtin:kubernetes.pods
  :filter(eq("k8s.cluster.name","preproduction"))
  :splitBy("dt.entity.cloud_application")
  :max"""

metric_selector_list = ['builtin:host.cpu.usage:max',
                        'builtin:host.cpu.usage:fold(max)',
                        'builtin:host.cpu.usage:splitBy()',
                        'builtin:kubernetes.pods:filter(eq("k8s.cluster.name","preproduction")):splitBy("dt.entity.cloud_application"):max']

metric_selector_file_path = 'metric_selectors.txt'


# NEW IDEA!


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
        print()
        parsed_metric_selectors_text_area = dt_metrics.parse_metric_selectors_text_area(metric_selectors_from_file)
        self.assertEqual(['builtin:host.cpu.usage:merge(0):avg'],
                         dt_metrics.parse_metric_selectors_text_area(metric_selector))
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
        default_time = util.default_time()
        print(f'from_time: {from_time}')
        print(f'from_time_utc: {from_time_utc}')
        print(f'start_timestamp: {start_timestamp}')
        print(f'deftault_time: {default_time}')

    def test_metric_request(self):
        print()
        script_location: Path = Path(__file__).resolve()

        # Calculate the absolute path of the directory containing the pickle files
        # This assumes that the pickle directory is in the same directory as the current script
        pickle_path: Path = script_location.parent / "pickle_requests"
        prefix: str = "response_https__fbk23429livedynatracecom_api_v2_"
        file_name: str = "metrics_1687888114.pkl"

        metrics_response: MetricDescriptorCollection = pickle.load(open(Path(pickle_path, prefix + file_name), 'rb'))

        # Metric descriptor returned from call to /api/v2/metrics/{metricKey}
        metric_descriptor_request = pickle.load(open(Path(pickle_path,
                                                          "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"),
                                                     'rb'))
        metric_descriptor_response = pickle.load(open(Path(pickle_path,
                                                           "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"),
                                                      'rb'))

        expected_json = [{'aggregationTypes': ['auto', 'value'],
                          'metricId': 'builtin:billing.ddu.events.byDescription',
                          'unit': 'Unspecified'},
                         {'aggregationTypes': ['auto', 'value'],
                          'metricId': 'builtin:billing.ddu.events.byEntity',
                          'unit': 'Unspecified'},
                         {'aggregationTypes': ['auto', 'value'],
                          'metricId': 'builtin:billing.ddu.events.total',
                          'unit': 'Unspecified'},
                         {'aggregationTypes': ['auto', 'value'],
                          'metricId': 'builtin:billing.ddu.log.byDescription',
                          'unit': 'Unspecified'}]
        parsed_response = util.parse_dynatrace_response(metrics_response, Endpoint.METRICS)
        self.assertEqual(expected_json, parsed_response)

        metric_id = pickle.load(open(Path(pickle_path,
                                          "response_https__fbk23429livedynatracecom_api_v2_metrics_builtinbillingddulogbyDescription_1687888114.pkl"),
                                     'rb'))
        pprint(util.parse_dynatrace_response(metric_id, Endpoint.METRICS_QUERY))

        raw_metrics = pickle.load(
            open(Path(pickle_path, "response_https__fbk23429livedynatracecom_api_v2_metrics_query_1687888114.pkl"),
                 'rb'))

    def test_process_timeseries_data(self):
        time_series_data = []
        parsed_data = {}
        for file_name, file_type, timestamp, url, data in sorted(pickled_test_inputs()):
            endpoint = get_endpoint_info(url)
            if endpoint == Endpoint.METRICS_QUERY and file_type == "response":
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
                    time_series_data.append(data_point)

                series_count = parsed_data['totalCount']
                print(f'time_series_data: {time_series_data}')
                # Get the number of unique descriptions in the list of dicts
                series_in_list = set([item.get('Description') for item in time_series_data])
                series_in_list_count = len(series_in_list)
                print(f'series_count: {series_count}')
                print(f'series_in_list: {series_in_list}')
                print(f'len(series_in_list): {len(series_in_list)}')

                if series_count != series_in_list_count:
                    for item in time_series_data:
                        if item.get('Description') == 'None':
                            print(f'item: {item}')

                self.assertEqual(series_count, series_in_list_count)

    def test_build_event_data(self):
        print()
        metric_descriptor: MetricDescriptor
        opt_dynatrace_tenant: Tenant
        metric_id: MetricId
        metric_selector_used: MetricSelector
        tenant: Tenant
        event_data: list[DataPoint] = []
        example_data = {'Description': 'Business events Query', 'timestamp': 1690295340000, 'value': None,
                        'resolution': '1m', 'metric_name': 'builtin:billing.ddu.events.byDescription',
                        'dynatraceTenant': 'https://jlw10381.live.dynatrace.com',
                        'metric_selector_used': 'builtin:billing.ddu.events.byDescription', 'unit': 'Unspecified'}

        for file_name, file_type, timestamp, url, data in sorted(pickled_test_inputs()):
            endpoint = get_endpoint_info(url)
            if endpoint == Endpoint.METRIC_DESCRIPTORS and file_type == "response":
                metric_descriptor = util.parse_dynatrace_response(data.json(), endpoint)
                # This is a hack to get the metric_selector used in the request
                # This is only needed for customer convenience, correlating which Splunk input created the  ouput data
                metric_selector_used = MetricSelector(url.split('/')[-1])
                # Get the first three parts of the URL, which is the tenant
                tenant = Tenant('/'.join(url.split('/')[:3]))
                metric_id = metric_descriptor['metricId']
                print(f'metric_descriptor: {metric_descriptor}')
                print(f'metric_id: {metric_id}')
                print(f'metric_selector_used: {metric_selector_used}')
                print(f'tenant: {tenant}')

                # TODO: Find metric_selector

            if endpoint == Endpoint.METRICS_QUERY and file_type == "response":
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
                    point = dt_metrics.build_event_data(data_point, metric_descriptor, tenant,
                                                             metric_selector_used)
                    event_data.append(point)
                    for key in example_data:
                        self.assertIn(key, example_data.keys())

    def test_metric_execute_session(self):
        print()
        metric_selectors: list[MetricSelector] = dt_metrics.parse_metric_selectors_text_area(metric_selectors_from_file)
        secrets = util.parse_secrets_env()
        time = util.get_from_time(60)
        tenant = secrets['dynatrace_tenant']
        api_token = secrets['dynatrace_api_token']

        metric_descriptor_list: list[MetricDescriptorCollection] = util.execute_session(Endpoint.METRICS, tenant, api_token, Params({}), metric_selectors)

        metric_descriptor_mapping = {}
        for metric_descriptor in metric_descriptor_list:
            metrics = metric_descriptor.get('metrics')
            for metric in metrics:
                metric_id = metric.get('metricId')
                unit = metric.get('unit')
                aggregation_types = metric.get('aggregationTypes')
                metric_descriptor_mapping[metric_id] = (unit, aggregation_types)

        params = {'time': time}

        metric_data_list: list[MetricData] = list(util.execute_session(Endpoint.METRICS_QUERY, tenant, api_token, params, metric_selectors))
        print(f'metric_data_list: {metric_data_list}')

        for metric_data in metric_data_list:
            result = metric_data.get('result')
            resolution = metric_data.get('resolution')
            for metric_series_collection in result:
                metric_id = metric_series_collection.get('metricId')
                data = metric_series_collection.get('data')
                unit, aggregation_types = metric_descriptor_mapping.get(metric_id, (None, None))
                for metric_series in data:
                    for timestamp, value in zip(metric_series.get('timestamps'), metric_series.get('values')):
                        print({
                            'timestamp': timestamp,
                            'value': value,
                            'metric_id': metric_id,
                            'unit': unit,
                            'aggregation_types': aggregation_types,
                            'dynatraceTenant': tenant,
                            'resolution': resolution
                        })


if __name__ == '__main__':
    unittest.main()
