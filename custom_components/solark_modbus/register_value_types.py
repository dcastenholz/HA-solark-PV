"""Register value type aliases for SolArk."""

import datetime
from typing import Protocol, Self, TypeVar, Union

from homeassistant.helpers.entity import EntityDescription

# class EntityDescriptionFactory(EntityDescription, Protocol):
#     @classmethod
#     def from_kwargs(
#         cls,
#         *,
#         key: str,
#         name: str,
#         entry_class: type,
#         opts: dict,
#     ) -> Self: ...


# TODO - Cleanup any combinable  types.
NumericValue = Union[int, float]
SensorValue = Union[int, float, str, datetime.datetime, None]
KeyValue = Union[int, str, bool]
RegisterValue = int

TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription)
TSensorValue = TypeVar("TSensorValue", int, float, str, bool)
TNumericRegisterValue = TypeVar("TNumericRegisterValue", int, float, str)
TMappedSensorValue = TypeVar("TMappedSensorValue", int, str, bool)
