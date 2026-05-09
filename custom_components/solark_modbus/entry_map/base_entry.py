"""Base class for all SolArk entities."""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, Self, TypedDict, Union, cast

from homeassistant.const import EntityCategory
from typing_extensions import Unpack

from ..register_value_types import NumericValue, TEntityDescription, TSensorValue

if TYPE_CHECKING:
    from ..data import SolArkData

_LOGGER = logging.getLogger(__name__)


class BaseEntryOptional(TypedDict, total=False):
    """Optional keyword arguments shared by all map entries."""

    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool

    set_sensor_value: Callable[[Any, "SolArkData"], None]


class EntityDescriptionFactory(Protocol):
    @classmethod
    def from_kwargs(
        cls,
        *,
        key: str,
        name: str,
        entry_class: type,
        opts: dict,
    ) -> Self: ...


class BaseEntry(Generic[TEntityDescription, TSensorValue], ABC):
    """
    BaseEntry[TEntityDescription, TSensorValue]

        Type Parameters:
            TEntityDescription: the entity description type.
            TSensorValue: the type of the sensor display value.

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
    ENTITY_DESCRIPTION_CLS: type[EntityDescriptionFactory]
    # ENTITY_DESCRIPTION_CLS: ClassVar[type[TEntityDescription]]

    # Holds the final value sent to the sensor for display in the UI.
    # The UI can do further processing on the actual displayed value as well as the icon shown.
    _sensor_value: TSensorValue | None = None

    set_sensor_value: Callable[[Self, "SolArkData"], None] | None

    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseEntryOptional]) -> None:
        """Initialize the map entry."""
        self.key = key
        self.name = name

        # Merge any DEFAULTS class properties with kwargs
        self.opts = {**self._merged_defaults, **kwargs}

        # -----------------------------
        # Store fields using kwargs merged with DEFAULTS
        # -----------------------------
        self.set_sensor_value = self.opts.get("set_sensor_value")

        self._entity_description = self._create_entity_description(self.__class__)

    def __init_subclass__(cls, **kwargs):
        """Merge defaults from the inheritance chain for each subclass."""
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

    # @abstractmethod
    def _create_entity_description(self, entry_class: type[BaseEntry]) -> TEntityDescription:
        """Subclasses must construct the entity description."""
        return cast(TEntityDescription, self.ENTITY_DESCRIPTION_CLS.from_kwargs(
            key=self.key,
            name=self.name,
            entry_class=entry_class,
            opts=self.opts,
        ))

    # -----------------------------
    # Entity access
    # -----------------------------
    @property
    def entity_description(self) -> TEntityDescription:
        """Return the entity description for this entry."""
        return self._entity_description

    @entity_description.setter
    def entity_description(self, value: TEntityDescription) -> None:
        """Set the entity description for this entry."""
        self._entity_description = value

    @property
    def sensor_value(self) -> TSensorValue | None:
        """Return the processed sensor value."""
        return self._sensor_value

    @sensor_value.setter
    def sensor_value(self, value: TSensorValue):
        """Set the processed sensor value."""
        self._sensor_value = value

    def calc_sensor_value(self: Self, runtime_data: "SolArkData") -> None:
        """Overridable method to calculate and store this entry's sensor value."""
        return

    def process_sensor_value(self: Self, runtime_data: "SolArkData"):
        """Process this entry's sensor value using a custom hook or default logic."""
        if self.set_sensor_value is not None:
            self.set_sensor_value(self, runtime_data)
        else:
            self.calc_sensor_value(runtime_data)

    # -----------------------------
    # Validation hook
    # -----------------------------
    def _validate(self) -> None:
        """
        Base validation for all entries.
        Subclasses may extend this.
        """
        return

    # @classmethod
    # @abstractmethod
    # def dynamic_icon(cls, lookup_map_key: TSensorValue) -> str | None:
    #     """Return a dynamic icon for the value if one is configured."""
    #     pass

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


class BaseRegisterEntry(Generic[TEntityDescription, TSensorValue], BaseEntry[TEntityDescription, TSensorValue], ABC):
    """
    RegisterEntry[TSensorValue]

        Type Parameters:
            TSensorValue: the type of the sensor display value.

    Abstract base class for all modbus register-backed sensors.

        Adds:
            the register address for the start of the range to read
            the length of the register range to read
            storage of decoded register read value
            validation
    """

    address: int

    def __init__(self, address: int, key: str, name: str, **kwargs) -> None:
        """Initialize a register-backed entry."""
        super().__init__(key, name, **kwargs)

        self.address = address

    @property
    @abstractmethod
    def register_length(self) -> int:
        """Return the number of Modbus registers to read."""
        pass

    def _validate(self):
        # RegisterEntry must have non-negative address
        if self.address < 0:
            raise ValueError(f"RegisterEntry {self._entity_description.key}: address must be >= 0")
