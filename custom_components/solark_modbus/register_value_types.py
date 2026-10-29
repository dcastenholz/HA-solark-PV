"""Register value type aliases for SolArk."""

# pylint: disable=invalid-name

import datetime
from typing import Any, Generic, Protocol, TypeVar, Union

from homeassistant.helpers.entity import EntityDescription

# TODO - Cleanup any combinable  types.
NumericValue = Union[int, float]
SensorValue = Union[int, float, str, datetime.datetime, None]
KeyValue = Union[int, str, bool]
RegisterValue = int


TEntityDescription = TypeVar(
    "TEntityDescription",
    bound=EntityDescription,
)

TEntityDescription_co = TypeVar(
    "TEntityDescription_co",
    bound=EntityDescription,
    covariant=True,
)

TSensorValue = TypeVar("TSensorValue", int, float, str, bool)
TNumericRegisterValue = TypeVar("TNumericRegisterValue", int, float, str)
TMappedSensorValue = TypeVar("TMappedSensorValue", int, str, bool)

EntryT_contra = TypeVar("EntryT_contra", bound=type[Any], contravariant=True)

class EntityDescriptionFactory(Protocol, Generic[TEntityDescription_co, EntryT_contra]):
    """Protocol for factory that creates entity descriptions from entry options."""
    @classmethod
    def from_kwargs(
        cls,
        *,
        key: str,
        name: str | None,
        entry_class: EntryT_contra,
        opts: dict[str, Any],
    ) -> TEntityDescription_co:
        ...

TEntityDescriptionFactory = TypeVar("TEntityDescriptionFactory", bound=EntityDescriptionFactory[Any, Any])
