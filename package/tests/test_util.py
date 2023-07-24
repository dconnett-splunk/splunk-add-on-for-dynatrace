import pathlib
from unittest import mock
from requests.models import Response
import package.bin.util as util
import unittest
from package.bin.util import V2Endpoints


def request_info_generator():
    time = util.get_from_time()
    tenant = "test_tenant"
    api_token = "test_token"

    for enum in V2Endpoints:
        endpoint = enum
        # Expected url after formatting
        params = {}
        expected_url = tenant + endpoint.url
        entity_types = ["HOST", "SERVICE", "APPLICATION", "PROCESS_GROUP", "PROCESS_GROUP_INSTANCE"]

        if endpoint.url_param_map:
            params = {endpoint.url_param_map: "Computer1234"}
            expected_url = expected_url.format(id=params[endpoint.url_param_map])

        yield endpoint, tenant, api_token, time, params, entity_types, expected_url

class TestMetricsUtil(unittest.TestCase):
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

    def test_get_dynatrace_data(self):
        for endpoint, tenant, api_token, time, params, entity_types, expected_url in request_info_generator():
            requests_info = util.prepare_dynatrace_request(endpoint, tenant, api_token, time=time, params=params,
                                                           entity_types=entity_types)

            print()
            print(f"requests_info: {requests_info}")
            for url, headers, params, selector in requests_info:
                print()
                print(f"url: {url}")
                print(f"headers: {headers}")
                print(f"params: {params}")
                print(f"selector: {selector}")


            # Create a mock response
            mock_response = Response()
            mock_response.status_code = 200
            mock_response._content = b'{"key": "value"}'  # Set the content to be some JSON

            # Create a mock session
            mock_session = mock.Mock()
            mock_session.get.return_value = mock_response

            # Now when get_dynatrace_data calls session.get, it will get the mock response
            result = util.get_dynatrace_data(mock_session, requests_info)
            print(f"result: {result}")

            # You can now assert that the result is what you expect
            self.assertEqual(result, result)  # replace ... with the expected result


if __name__ == '__main__':
    unittest.main()
