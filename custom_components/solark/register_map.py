import logging
from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar

from homeassistant.const import EntityCategory

from .register_map_entry import RegisterMapEntry, RegisterValue
from .sensor_entity_description import SolArkModbusSensorEntityDescription

_LOGGER = logging.getLogger(__name__)

# ----------------------------------
# Type variable for the real subclass
# ----------------------------------
T = TypeVar("T", bound="RegisterMap")


# ----------------------------------
# Register Map
# ----------------------------------
@dataclass
class RegisterMap(Generic[T]):
    """Base class for register maps that collects RegisterMapEntry class attributes across inheritance."""

    def __init__(self):
        # Collect all RegisterMapEntry attributes from the class and parent classes
        entries_to_sort: dict[str, "RegisterMapEntry"] = {}

        # Collect all RegisterMapEntry attributes from the base and derived classes.
        # Iterate the class hierarchy (MRO) from base → derived so that derived
        # class entries override any entries with the same name from the base class.
        for cls in reversed(self.__class__.__mro__):
            for attr_name, attr_value in cls.__dict__.items():
                if isinstance(attr_value, RegisterMapEntry):
                    entries_to_sort[attr_name] = attr_value

        # Sorted list of entries by address
        self._sorted: list["RegisterMapEntry"] = sorted(entries_to_sort.values(), key=lambda e: e.address)

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

        # Error flag
        self._error: bool = False

    # TODO - deduplicate this with __init__ and __init_subclass__. We should be able to just do this in __init_subclass__ and
    #  then the instance can just copy the class-level _map and _sorted to instance-level variables if needed.
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Collect all RegisterMapEntry class attributes
        entries = {name: value for name, value in cls.__dict__.items() if isinstance(value, RegisterMapEntry)}
        cls._map = entries
        cls._sorted = sorted(entries.values(), key=lambda e: e.address)
        cls._error = False

    def get_entry(self, key: str) -> "RegisterMapEntry | None":
        """Get a RegisterMapEntry by key."""
        return self._map.get(key)

    def get_descriptions(self) -> list[SolArkModbusSensorEntityDescription]:
        return [
            entry.from_register_map_entry()
            for entry in self._sorted
            # Modern HA does not use EntityCategory.CONFIG for sensors.
            if entry.entity_description.entity_category != EntityCategory.CONFIG
        ]

    def is_error(self) -> bool:
        """Return whether an error occurred."""
        return self._error

    def set_error(self, value: bool = True):
        """Set error flag."""
        self._error = value

    def __getitem__(self, key: str) -> "RegisterMapEntry":
        return self._map[key]

    def __iter__(self) -> Iterator["RegisterMapEntry"]:
        return iter(self._sorted)

    def as_dict(self) -> dict[str, "RegisterValue"]:
        return {entry.entity_description.key: entry.register_value for entry in self._sorted}

    def is_empty(self) -> bool:
        return len(self._map) == 0

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
