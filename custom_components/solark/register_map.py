import logging
from typing import Iterator

from homeassistant.const import EntityCategory

from .register_map_entry import RegisterMapEntry
from .sensor_entity_description import SolArkModbusSensorEntityDescription
from .sensor_map_entry import RegisterValue

_LOGGER = logging.getLogger(__name__)

# ----------------------------------
# Type variable for the real subclass
# ----------------------------------
# T = TypeVar("T", bound="RegisterMap")


# ----------------------------------
# Register Map
# ----------------------------------
class RegisterMap:
    """Base class for register maps that collects RegisterMapEntry class attributes across inheritance."""

    _entries: list[RegisterMapEntry]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Collect all SensorMapEntry attributes from the class and parent classes
        # Walk full inheritance chain
        cls._entries = [
            value
            for base in reversed(cls.__mro__)
            for value in base.__dict__.values()
            if isinstance(value, RegisterMapEntry)
        ]

    def __init__(self):
        # Instance just references class-level data
        self._entries = self.__class__._entries
        self._error = False
        self._sort()
        self._validate()

    def _sort(self):
        self._entries.sort(key=lambda e: e.address)

    def _validate(self):
        # Ensure no overlapping address ranges
        prev = None
        for entry in self:
            if prev is not None:
                prev_end = prev.address + prev.register_length - 1
                if entry.address <= prev_end:
                    raise ValueError(
                        f"Register overlap detected: "
                        f"{prev} [{prev.address}-{prev_end}] overlaps "
                        f"{entry} [{entry.address}-{entry.address + entry.register_length - 1}]"
                    )
            prev = entry


    def get_descriptions(self) -> list[SolArkModbusSensorEntityDescription]:
        return [
            entry.entity_description
            for entry in self._entries
            # Modern HA does not use EntityCategory.CONFIG for sensors.
            if entry.entity_description.entity_category != EntityCategory.CONFIG
        ]

    def is_error(self) -> bool:
        """Return whether an error occurred."""
        return self._error

    def set_error(self, value: bool = True):
        """Set error flag."""
        self._error = value

    def __iter__(self) -> Iterator["RegisterMapEntry"]:
        return iter(self._entries)

    def as_dict(self) -> dict[str, RegisterValue]:
        return {entry.entity_description.key: entry.register_value for entry in self._entries}

    def init(self):
        """Initialize the register map before reading registers."""
        self.set_error(False)

    def init_register_range(self, start: RegisterMapEntry, end: RegisterMapEntry | None = None):
        """Initialize the register map entries in the range before reading."""
        entries = self.entries_register_read_in_range(start, end)

        for entry in entries:
            entry.register_value = None

    #
    # Iterators
    #
    def entries_register_read_in_range(self, start: RegisterMapEntry, end: RegisterMapEntry | None = None) -> Iterator[RegisterMapEntry]:
        """Yield registers from start to end (inclusive). If end is None, yield only start."""
        end = end or start  # if end is None, just use start

        for entry in self:
            if entry.address < start.address:
                continue
            if entry.address > end.address:
                break
            yield entry
