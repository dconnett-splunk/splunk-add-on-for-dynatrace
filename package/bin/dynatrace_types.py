from dataclasses import dataclass
import json
import typing


@dataclass
class DynatraceMetricSelector:
    selector: str


@dataclass
class DynatraceSyntheticLocation:
    capabilities: list[str]
    cloudPlatform: str
    endpoint: str
    entityId: str
    geoLocationId: str
    ips: list[str]
    name: str
    stage: str
    status: str
    type: str


@dataclass
class DynatraceProblem:
    json: str


@dataclass
class DynatraceMetric:
    metric_name: str
    resolution: str
    unit: str
    timestamp: str
    value: str
    dynatraceTenant: str
    metricSelector: str


@dataclass
class DynatraceSyntheticExecution:
    json: str


@dataclass
class DynatraceSyntheticMonitor:
    json: str
