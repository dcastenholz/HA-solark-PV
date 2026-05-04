"""Register value type aliases for SolArk."""

import datetime
from typing import TypeVar, Union

from homeassistant.helpers.entity import EntityDescription

# TODO - Cleanup any combinable  types.
NumericValue = Union[int, float]
SensorValue = Union[int, float, str, datetime.datetime, None]
KeyValue = Union[int, str, bool]
RegisterValue = int

TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription)
TSensorValue = TypeVar("TSensorValue", int, float, str, bool)
TNumericRegisterValue = TypeVar("TNumericRegisterValue", int, float, str)
TMappedSensorValue = TypeVar("TMappedSensorValue", int, str, bool)
