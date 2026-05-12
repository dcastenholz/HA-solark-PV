"""Register value type aliases for SolArk."""

import datetime
from typing import Any, Generic, Protocol, Self, Type, TypeVar, Union

from homeassistant.helpers.entity import EntityDescription

TEntryClass = TypeVar("TEntryClass")

class EntityDescriptionFactory(Protocol, Generic[TEntryClass]):
    @classmethod
    def from_kwargs(
        cls,
        *,
        key: str,
        name: str | None,
        entry_class: Type[TEntryClass],
        opts: dict[str, Any],
    ) -> Self: ...

# TODO - Cleanup any combinable  types.
NumericValue = Union[int, float]
SensorValue = Union[int, float, str, datetime.datetime, None]
KeyValue = Union[int, str, bool]
RegisterValue = int

TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription)
# TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescriptionFactory[Any])
TEntityDescriptionFactory = TypeVar(
    "TEntityDescriptionFactory",
    bound=EntityDescriptionFactory[Any],
)
# TEntryClass = TypeVar("TEntryClass", BaseSensorEntry, BaseBinarySensorEntry)
TSensorValue = TypeVar("TSensorValue", int, float, str, bool)
TNumericRegisterValue = TypeVar("TNumericRegisterValue", int, float, str)
TMappedSensorValue = TypeVar("TMappedSensorValue", int, str, bool)
