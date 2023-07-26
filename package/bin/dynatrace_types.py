from dataclasses import dataclass
import json
import typing
from typing import TypedDict, NewType, Dict, List, Any, Union, Set, Type
from datetime import date

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
Dimension = NewType('Dimension', Union[EntityID, str])
DimensionType = NewType('DimensionType', str)
MetricId = NewType('MetricId', str)
LocationId = NewType('locationId', str)
ExecutionId = NewType('executionId', str)


class Rollup(TypedDict):
    parameter: float
    type: str


class Filter:
    referenceInvocation: dict
    targetDimension: str
    targetDimensions: List[str]
    referenceString: str
    rollup: str
    referenceValue: float
    operands: List[dict]
    type: str


class AppliedFilter(TypedDict):
    appliedTo: list[str]
    filter: Filter


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
    metricId: MetricId
    metricSelector: MetricSelector
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


class DimensionMap(TypedDict):
    dimensionType: DimensionType
    dimension: Dimension


class DataPoint(TypedDict):
    "Splunk type"
    dimensionMap: DimensionMap
    timestamp: date
    value: Any
    resolution: str


class MetricSeries(TypedDict):
    dimensionMap: DimensionMap
    timestamps: list[date]
    values: list[Any]
    dimensions: Set[Dimension]


class MetricSeriesCollection(TypedDict):
    dataPointCountRatio: float
    dimensionCountRatio: float
    appliedOptionalFilters: list[dict]
    metricId: MetricId
    warnings: list[str]
    data: list[MetricSeries]


class MetricData(TypedDict):
    resolution: str
    totalCount: int
    nextPageKey: str
    warnings: list[str]
    result: list[MetricSeriesCollection]


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
    "Splunk type"
    "TODO Probably want to change this"
    metric_name: str
    resolution: str
    unit: str
    timestamp: date
    value: str
    dynatraceTenant: str
    metricSelector: MetricSelector


class LocationExecutionResults(TypedDict):
    locationId: LocationId
    executionId: ExecutionId
    requestResults: list[dict]


class MonitorExecutionResults(TypedDict):
    locationExecutionResults: list[LocationExecutionResults]
    monitorId: str


class SyntheticExecution(TypedDict):
    json: str


class SyntheticMonitor(TypedDict):
    json: str


class Entity(TypedDict):
    lastSeenTms: int
    firstSeenTms: int
    entityId: EntityID
    managementZones: list[dict]
    toRelationships: dict
    fromRelationships: dict
    tags: list[dict]
    icon: dict
    displayName: str
    properties: dict
    type: str


class EntitiesList(TypedDict):
    totalCount: int
    pageSize: int
    nextPageKey: str
    entities: list[Entity]


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
