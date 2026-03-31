import logging
from typing import Iterator

from homeassistant.const import EntityCategory

from .sensor_entity_description import SolArkModbusSensorEntityDescription
from .sensor_map_entry import RegisterValue, SensorMapEntry

_LOGGER = logging.getLogger(__name__)

# ----------------------------------
# Type variable for the real subclass
# ----------------------------------
# T = TypeVar("T", bound="SensorMap")


# ----------------------------------
# Register Map
# ----------------------------------
class SensorMap:
    """Base class for register maps that collects SensorMapEntry class attributes across inheritance."""

    _entries: list[SensorMapEntry]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Collect all SensorMapEntry attributes from the class and parent classes
        # Walk full inheritance chain
        cls._entries = [
            value
            for base in reversed(cls.__mro__)
            for value in base.__dict__.values()
            if isinstance(value, SensorMapEntry)
        ]

    def __init__(self):
        # Instance just references class-level data
        self._entries = self.__class__._entries
        self._error = False
        self._sort()
        self._validate()

    def _sort(self):
        return

    def _validate(self):
        return

    def get_descriptions(self) -> list[SolArkModbusSensorEntityDescription]:
        return [
            entry.entity_description
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

    def __iter__(self) -> Iterator["SensorMapEntry"]:
        return iter(self._entries)

    def as_dict(self) -> dict[str, RegisterValue]:
        return {entry.entity_description.key: entry.register_value for entry in self._entries}

    def init(self):
        """Initialize the register map before reading registers."""
        self.set_error(False)
