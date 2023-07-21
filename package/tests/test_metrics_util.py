import package.bin.metrics_util as dt_metrics
from unittest import TestCase
from pprint import pprint
import json
from pathlib import Path

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


