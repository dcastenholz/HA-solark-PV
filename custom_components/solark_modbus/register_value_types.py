"""Register value type aliases for SolArk."""

import datetime
from typing import Any, Generic, Protocol, TypeVar, Union

from homeassistant.helpers.entity import EntityDescription

# TODO - Cleanup any combinable  types.
NumericValue = Union[int, float]
SensorValue = Union[int, float, str, datetime.datetime, None]
KeyValue = Union[int, str, bool]
RegisterValue = int

TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription, covariant=True) # pylint: disable=invalid-name disable=typevar-name-incorrect-variance
TSensorValue = TypeVar("TSensorValue", int, float, str, bool)   # pylint: disable=invalid-name
TNumericRegisterValue = TypeVar("TNumericRegisterValue", int, float, str)   # pylint: disable=invalid-name
TMappedSensorValue = TypeVar("TMappedSensorValue", int, str, bool)  # pylint: disable=invalid-name

EntryT = TypeVar("EntryT", bound=type[Any], contravariant=True) # pylint: disable=typevar-name-incorrect-variance

class EntityDescriptionFactory(Protocol, Generic[TEntityDescription, EntryT]):
    """Protocol for factory that creates entity descriptions from entry options."""
    @classmethod
    def from_kwargs(
        cls,
        *,
        key: str,
        name: str | None,
        entry_class: EntryT,
        opts: dict[str, Any],
    ) -> TEntityDescription:
        ...

TEntityDescriptionFactory = TypeVar("TEntityDescriptionFactory", bound=EntityDescriptionFactory[Any, Any])  # pylint: disable=invalid-name
