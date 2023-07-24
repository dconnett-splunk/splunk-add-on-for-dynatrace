from dataclasses import dataclass
import json
import typing
from typing import TypedDict, NewType, Dict

"""dduBillable	boolean	
If true the usage of metric consumes Davis data units. Deprecated and always false for Dynatrace Platform Subscription. Superseded by isBillable.

Metric expressions don't return this field.

billable	boolean	
If truethe usage of metric is billable.

Metric expressions don't return this field.

lastWritten	integer	
The timestamp when the metric was last written.

Has the value of null for metric expressions or if the data has never been written.

impactRelevant	boolean	
The metric is (true) or is not (false) impact relevant.

An impact-relevant metric is highly dependent on other metrics and changes because an underlying root-cause metric has changed.

Metric expressions don't return this field.

minimumValue	number	
The minimum allowed value of the metric.

Metric expressions don't return this field.

maximumValue	number	
The maximum allowed value of the metric.

Metric expressions don't return this field.

latency	integer	
The latency of the metric, in minutes.

The latency is the expected reporting delay (for example, caused by constraints of cloud vendors or other third-party data sources) between the observation of a metric data point and its availability in Dynatrace.

The allowed value range is from 1 to 60 minutes.

Metric expressions don't return this field.

resolutionInfSupported	boolean	
If 'true', resolution=Inf can be applied to the metric query.

unitDisplayFormat	string	
The raw value is stored in bits or bytes. The user interface can display it in these numeral systems:

Binary: 1 MiB = 1024 KiB = 1,048,576 bytes

Decimal: 1 MB = 1000 kB = 1,000,000 bytes

If not set, the decimal system is used.

Metric expressions don't return this field.

The element can hold these values
dimensionCardinalities	MetricDimensionCardinality[]	
The cardinalities of MINT metric dimensions.

defaultAggregation	MetricDefaultAggregation	
The default aggregation of a metric.

rootCauseRelevant	boolean	
The metric is (true) or is not (false) root cause relevant.

A root-cause relevant metric represents a strong indicator for a faulty component.

Metric expressions don't return this field.

dimensionDefinitions	MetricDimensionDefinition[]	
The fine metric division (for example, process group and process ID for some process-related metric).

For ingested metrics, dimensions that doesn't have have any data within the last 15 days are omitted.

entityType	string[]	
List of admissible primary entity types for this metric. Can be used for the type predicate in the entitySelector.

metricId	string	
The fully qualified key of the metric.

If a transformation has been used it is reflected in the metric key.

metricSelector	string	
The metric selector that is used when querying a func: metric.

scalar	boolean	
Indicates whether the metric expression resolves to a scalar (true) or to a series (false). A scalar result always contains one data point. The amount of data points in a series result depends on the resolution you're using.

aggregationTypes	string[]	
The list of allowed aggregations for this metric.

The element can hold these values
metricValueType	MetricValueType	
The value type for the metric.

created	integer	
The timestamp of metric creation.

Built-in metrics and metric expressions have the value of null.

transformations	string[]	
Transform operators that could be appended to the current transformation list.

The element can hold these values
unit	string	
The unit of the metric.

warnings	string[]	
A list of potential warnings that affect this ID. For example deprecated feature usage etc.

tags	string[]	
The tags applied to the metric.

Metric expressions don't return this field.

displayName	string	
The name of the metric in the user interface.

description	string	
A short description of the metric.

"""
class MetricDescriptor(TypedDict):
    dduBillable: bool
    billable: bool
    lastWritten: int
    impactRelevant: bool
    minimumValue: float
    maximumValue: float
    latency: int
    resolutionInfSupported: bool
    unitDisplayFormat: str
    dimensionCardinalities: list[dict]
    defaultAggregation: str
    rootCauseRelevant: bool
    dimensionDefinitions: list[dict]
    entityType: list[str]
    metricId: str
    metricSelector: str
    scalar: bool
    aggregationTypes: list[str]
    metricValueType: str
    created: int
    transformations: list[str]
    unit: str
    warnings: list[str]
    tags: list[str]
    displayName: str
    description: str


class MetricDescriptorCollection(TypedDict):
    totalCount: int
    nextPageKey: str
    warnings: list[str]
    metrics: list[MetricDescriptor]


MetricSelector = NewType('MetricSelector', str)
APIToken = NewType('APIToken', str)
Tenant = NewType('Tenant', str)
EntityID = NewType('EntityID', str)
CollectionInterval = NewType('CollectionInterval', int)
WrittenSinceParam = NewType('WrittenSince', Dict[str, str])
StartTime = NewType('StartTime', int)
EndTime = NewType('EndTime', int)
URL = NewType('URL', str)
Params = NewType('Params', Dict[str, str])
ResponseSelector = NewType('ResponseSelector', str)



class SyntheticLocation(TypedDict):
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


class Problem(TypedDict):
    json: str


class Metric(TypedDict):
    metric_name: str
    resolution: str
    unit: str
    timestamp: str
    value: str
    dynatraceTenant: str
    metricSelector: str


class SyntheticExecution(TypedDict):
    json: str


class SyntheticMonitor(TypedDict):
    json: str


class Entity(TypedDict):
    json: str


class MetricDimensionCardinality(TypedDict):
    relative: float
    estimate: int
    key: str


class MetricDefaultAggregation(TypedDict):
    parameter: float
    type: str


class MetricDimensionDefinition(TypedDict):
    displayName: str
    name: str
    key: str
    type: str
    index: int


class MetricValueType(TypedDict):
    type: str
