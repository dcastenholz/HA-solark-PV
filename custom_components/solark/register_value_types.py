import datetime
from typing import TypeVar, Union

from homeassistant.helpers.entity import EntityDescription

NumericValue = Union[int, float]
SensorValue = Union[int, float, str, datetime.datetime, None]
KeyValue = Union[int, str, bool]
RegisterValue = int

TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription)
# TSensorValue = TypeVar("TSensorValue", int, float, str, bytes, bool)
TSensorValue = TypeVar("TSensorValue", int, float, str, bool)
TRegisterValue = TypeVar("TRegisterValue", int, float, str)
TNumericRegisterValue = TypeVar("TNumericRegisterValue", int, float, str)
TBaseValue = TypeVar("TBaseValue", int, float, str, bool)
TLookupMapKey = TypeVar("TLookupMapKey", int, float, str, bool)
TMappedSensorValue = TypeVar("TMappedSensorValue", int, str, bool)