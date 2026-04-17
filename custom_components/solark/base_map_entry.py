import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Generic, Self, TypedDict, TypeVar, Union

from homeassistant.components.sensor import EntityDescription
from homeassistant.const import EntityCategory
from typing_extensions import Unpack

from .register_value_types import NumericValue, SensorValue

if TYPE_CHECKING:
    from .data import SolArkData

_LOGGER = logging.getLogger(__name__)

TEntry = TypeVar("TEntry", bound="BaseMapEntry")
TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription)

class BaseMapEntryOptional(Generic[TEntry], TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool
    dynamic_icon: Callable[["SensorValue"], str | None]

    on_sensor_creating: Callable[[Any, "SolArkData"], None]

    on_data_updated: Callable[[Any, "SolArkData"], None]


class BaseMapEntry(Generic[TEntry, TEntityDescription], ABC):
    """
    Abstract base class for all SolArk map entries.

    Provides:
    - Entity metadata wrapper
    - Scaling and offset support
    - Post-processing hook
    - Numeric conversion helpers
    """
    DEFAULTS: dict[str, Any] = {
        "entity_registry_enabled_default": False,
    }

    _merged_defaults: dict[str, Any]

    opts: dict[str, Any] = {}

    key: str
    name: str
    _sensor_value: SensorValue = None
    _entity_description: TEntityDescription

    data_updated: Callable[[Self, "SolArkData"], None] | None

    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        self.key = key
        self.name = name

        # Set defaults in kwargs
        self.opts = {**self._merged_defaults, **kwargs}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # -----------------------------
        # MRO merge DEFAULTS once
        # -----------------------------
        merged: dict[str, Any] = {}

        for base in reversed(cls.mro()):
            defaults = getattr(base, "DEFAULTS", None)
            if defaults:
                merged.update(defaults)

        cls._merged_defaults = merged

    # -----------------------------
    # Entity access
    # -----------------------------
    @property
    def entity_description(self) -> TEntityDescription:
        return self._entity_description

    @entity_description.setter
    def entity_description(self, value: TEntityDescription) -> None:
        self._entity_description = value

    @property
    def sensor_value(self) -> SensorValue:
        return self._sensor_value

    @sensor_value.setter
    def sensor_value(self, value: SensorValue) -> None:
        self._sensor_value = value

    # -----------------------------
    # Validation hook
    # -----------------------------
    def _validate(self) -> None:
        """
        Base validation for all entries.
        Subclasses may extend this.
        """
        return

    # -----------------------------
    # Post processing
    # -----------------------------
    def on_data_updated(self: Self, runtime_data: "SolArkData") -> None:
        """ Execute post-processing method. """
        if self.data_updated:
            try:
                self.data_updated(self, runtime_data)
            except Exception:  # pylint: disable=broad-exception-caught
                _LOGGER.exception(
                    "Error while running data updated event of entry %s",
                    self._entity_description.key,
                )

    # -----------------------------
    # Numeric helpers
    # -----------------------------
    def _get_numeric(self) -> NumericValue:
        if isinstance(self.sensor_value, (int, float)):
            return self.sensor_value
        raise TypeError(
            f"Non-numeric register_value for {self._entity_description.key}: "
            f"{self.sensor_value}"
        )

    def __add__(self, other: Union[BaseMapEntry, NumericValue]) -> NumericValue:
        left = self._get_numeric()

        if isinstance(other, BaseMapEntry):
            return left + other._get_numeric()

        if isinstance(other, (int, float)):
            return left + other

        return NotImplemented

    def __radd__(self, other: NumericValue) -> NumericValue:
        if isinstance(other, (int, float)):
            return other + self._get_numeric()
        return NotImplemented

    def __int__(self) -> int:
        return int(self._get_numeric())

    def __float__(self) -> float:
        return float(self._get_numeric())

    def split_bytes_uint16(self) -> tuple[int, int]:
        """Split a UINT16 into two 8-bit integers (high byte, low byte)."""
        value: int = int(self)
        if not 0 <= value <= 0xFFFF:
            raise ValueError("Value must be in range 0..65535 (UINT16)")

        high = (value >> 8) & 0xFF
        low = value & 0xFF
        return high, low
