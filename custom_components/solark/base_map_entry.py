import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generic, Self, Tuple, TypedDict, Union

from homeassistant.const import EntityCategory
from typing_extensions import Unpack

from .register_value_types import NumericValue, SensorValue, TBaseValue, TEntityDescription, TLookupMapKey, TSensorValue

if TYPE_CHECKING:
    from .data import SolArkData

_LOGGER = logging.getLogger(__name__)


class BaseEntryOptional(TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool
    dynamic_icon: Callable[["SensorValue"], str | None]

    on_sensor_creating: Callable[[Any, "SolArkData"], None]
    on_data_updated: Callable[[Any, "SolArkData"], None]


class BaseEntry(Generic[TEntityDescription, TBaseValue, TSensorValue, TLookupMapKey], ABC):
    """
    BaseEntry[TEntityDescription, TBaseValue, TSensorValue]

        Type Parameters:
            TEntityDescription: the entity description type.
            TBaseValue: the type of the base value.
            TSensorValue: the type of the sensor display value.
            TLookupMapKey: the type of the dynamic lookup key value.

    Abstract base class for all sensors and binarysensors.

        Provides:
            entity description
            key
            name
            base value
            sensor value
    """

    DEFAULTS: dict[str, Any] = {
        "exclude_from_recorder": False,
        "entity_registry_enabled_default": False,
    }

    _merged_defaults: dict[str, Any]
    opts: dict[str, Any]

    key: str
    name: str
    _entity_description: TEntityDescription

    # _base_value holds the initial value from the source of truth
    _base_value: TBaseValue | None = None
    # _sensor_value holds the final value that will be displayed by the sensor
    _sensor_value: TSensorValue | None = None

    data_updated: Callable[[Self, "SolArkData"], None] | None

    # If LOOKUP_MAP is a non-empty dict, then it triggers dynamic lookup of icon and native_value for the sensor
    LOOKUP_MAP: dict[TSensorValue, Tuple[Any, str]] | None
    # dynamic_icon: Callable[[TLookupMapKey], str | None] | None = None
    # dynamic_sensor_value: Callable[[TLookupMapKey], TSensorValue | None] | None = None

    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseEntryOptional]) -> None:
        self.key = key
        self.name = name

        # Merge any DEFAULTS class properties with kwargs
        self.opts = {**self._merged_defaults, **kwargs}

        dynamic_opts: dict[str, Any] = {}

        dynamic_icon = self.opts.get("dynamic_icon")
        if dynamic_icon is None and self.is_dynamic_lookup():
            dynamic_opts["dynamic_icon"] = self.lookup_dynamic_icon

        dynamic_sensor_value = self.opts.get("dynamic_sensor_value")
        if dynamic_sensor_value is None and self.is_dynamic_lookup():
            dynamic_opts["dynamic_sensor_value"] = self.lookup_dynamic_sensor_value

        self.opts = {**self._merged_defaults, **dynamic_opts, **kwargs}

        # -----------------------------
        # Store fields using kwargs merged with DEFAULTS
        # -----------------------------
        self.data_updated = self.opts.get("on_data_updated")

        self._entity_description = self._create_entity_description()

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

    @abstractmethod
    def _create_entity_description(self) -> TEntityDescription:
        """Subclasses must construct the entity description."""

    @abstractmethod
    def dynamic_lookup_key(self, runtime_data: "SolArkData") -> TSensorValue | None:
        '''Needs to return the sensor_value'''

    @classmethod
    def is_dynamic_lookup(cls) -> bool:
        return getattr(cls, "LOOKUP_MAP", None) is not None

    @classmethod
    def lookup_dynamic_sensor_value(cls, lookup_map_key: TSensorValue) -> TSensorValue | None:
        '''This gets called in the sensor platform after the coordinator data is updated'''
        if cls.LOOKUP_MAP is None:
            return None

        if lookup_map_key is None:
            return None

        if lookup_map_key not in cls.LOOKUP_MAP:
            raise TypeError(f"Value {lookup_map_key!r} not valid for LOOKUP_MAP keys: {list(cls.LOOKUP_MAP.keys())}")

        return cls.LOOKUP_MAP[lookup_map_key][0] or None

    @classmethod
    def lookup_dynamic_icon(cls, lookup_map_key: TSensorValue) -> str | None:
        '''This gets called in the sensor platform after the coordinator data is updated'''
        if cls.LOOKUP_MAP is None:
            return None

        if lookup_map_key is None:
            return None

        if lookup_map_key not in cls.LOOKUP_MAP:
            raise TypeError(f"Value {lookup_map_key!r} not valid for LOOKUP_MAP keys: {list(cls.LOOKUP_MAP.keys())}")

        return cls.LOOKUP_MAP[lookup_map_key][1] or None

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
    def base_value(self) -> TBaseValue | None:
        return self._base_value

    @property
    def sensor_value(self) -> TSensorValue | None:
        return self._sensor_value

    def set_base_value(self, value: TBaseValue) -> None:
        self._base_value = value

    @abstractmethod
    def set_sensor_value(self: Self, runtime_data: "SolArkData") -> None:
        '''This method must end up setting the sensor_value'''

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
    # def post_process(self: Self, runtime_data: "SolArkData") -> None:
    #     """Execute post-processing across class hierarchy (base -> subclass)."""

    #     for cls in reversed(type(self).mro()):
    #         # Skip object base class
    #         if cls is object:
    #             continue

    #         # Only call if the class defines its own implementation
    #         method = cls.__dict__.get("_post_process")
    #         if method is None:
    #             continue

    #         # Avoid calling this same method recursively
    #         if method is BaseEntry.post_process:
    #             continue

    #         try:
    #             method(self, runtime_data)
    #         except Exception:  # pylint: disable=broad-exception-caught
    #             _LOGGER.exception(
    #                 "Error while running data updated event of entry %s (class %s)",
    #                 self._entity_description.key,
    #                 cls.__name__,
    #             )

    #     # Execute any post-processing static method that may be set by subclasses.
    #     if self.data_updated:
    #         try:
    #             self.data_updated(self, runtime_data)
    #         except Exception:  # pylint: disable=broad-exception-caught
    #             _LOGGER.exception(
    #                 "Error while running data updated event of entry %s",
    #                 self._entity_description.key,
    #             )

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

    def __add__(self, other: Union[BaseEntry, NumericValue]) -> NumericValue:
        left = self._get_numeric()

        if isinstance(other, BaseEntry):
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
