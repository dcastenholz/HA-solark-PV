import logging
from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar

from homeassistant.const import EntityCategory

from .sensor_entity_description import SolArkModbusSensorEntityDescription
from .sensor_map_entry import RegisterValue, SensorMapEntry

_LOGGER = logging.getLogger(__name__)

# ----------------------------------
# Type variable for the real subclass
# ----------------------------------
T = TypeVar("T", bound="SensorMap")


# ----------------------------------
# Register Map
# ----------------------------------
@dataclass
class SensorMap(Generic[T]):
    """Base class for register maps that collects SensorMapEntry class attributes across inheritance."""

    def __init__(self):
        # Collect all SensorMapEntry attributes from the class and parent classes
        entries: dict[str, "SensorMapEntry"] = {}

        # Collect all RegisterMapEntry attributes from the base and derived classes.
        # Iterate the class hierarchy (MRO) from base → derived so that derived
        # class entries override any entries with the same name from the base class.
        for cls in reversed(self.__class__.__mro__):
            for attr_name, attr_value in cls.__dict__.items():
                if isinstance(attr_value, SensorMapEntry):
                    entries[attr_name] = attr_value

        # Sorted list of entries by address
        self._entries: list["SensorMapEntry"] = list(entries.values())

    # TODO - deduplicate this with __init__ and __init_subclass__. We should be able to just do this in __init_subclass__ and
    #  then the instance can just copy the class-level _map and _sorted to instance-level variables if needed.
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Collect all SensorMapEntry class attributes
        entries = {name: value for name, value in cls.__dict__.items() if isinstance(value, SensorMapEntry)}
        cls._map = entries
        cls._entries = list(entries.values())
        cls._error = False

    def get_entry(self, key: str) -> "SensorMapEntry | None":
        """Get a SensorMapEntry by key."""
        return self._map.get(key)

    def get_descriptions(self) -> list[SolArkModbusSensorEntityDescription]:
        return [
            entry.from_register_map_entry()
            for entry in self._entries
            # Modern HA does not allow use EntityCategory.CONFIG for sensors.
            if entry.entity_description.entity_category != EntityCategory.CONFIG
        ]

    def is_error(self) -> bool:
        """Return whether an error occurred."""
        return self._error

    def set_error(self, value: bool = True):
        """Set error flag."""
        self._error = value

    def __getitem__(self, key: str) -> "SensorMapEntry":
        return self._map[key]

    def __iter__(self) -> Iterator["SensorMapEntry"]:
        return iter(self._entries)

    def as_dict(self) -> dict[str, "RegisterValue"]:
        return {entry.entity_description.key: entry.register_value for entry in self._entries}

    def is_empty(self) -> bool:
        return len(self._map) == 0

    def init(self):
        """Initialize the register map before reading registers."""
        self.set_error(False)
