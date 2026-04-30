''' Class for defining and processing entries that are read from registers.'''
from abc import ABC
from typing import Iterator

from .base_map import BaseMap
from .register_map_entry import RegisterEntry


class RegisterMap(BaseMap[RegisterEntry], ABC):
    '''Register map may contain only entries that are, or are a subclass of, RegisterEntry'''
    _entry_type = RegisterEntry

    # ---------- sorting ----------
    def _sort(self):
        self._entries.sort(key=lambda e: e.address)

    # ---------- validation ----------
    def _validate(self):
        # Ensure no overlapping address ranges
        prev = None
        for entry in self._entries:
            if prev is not None:
                prev_end = prev.address + prev.register_length - 1

                if entry.address <= prev_end:
                    raise ValueError(
                        f"Register overlap detected: "
                        f"{prev} [{prev.address}-{prev_end}] overlaps "
                        f"{entry} [{entry.address}-{entry.address + entry.register_length - 1}]"
                    )
            prev = entry

    def is_error(self) -> bool:
        """Return whether an error occurred."""
        return self._error

    def set_error(self, value: bool = True):
        """Set error flag."""
        self._error = value

    def init(self):
        """Initialize the register map before reading registers."""
        self.set_error(False)

    # ---------- register range helpers ----------
    def init_register_range(self, start: RegisterEntry, end: RegisterEntry | None = None):
        """Initialize the register map entries in the range before reading."""
        entries = self.entries_register_read_in_range(start, end)

        # TODO - Do we need to clear this somehow???
        # for entry in entries:
        #     entry.register_value = None

    def entries_register_read_in_range(self, start: RegisterEntry, end: RegisterEntry | None = None) -> Iterator[RegisterEntry]:
        """Yield registers from start to end (inclusive). If end is None, yield only start."""

        end = end or start

        for entry in self._entries:
            if entry.address < start.address:
                continue
            if entry.address > end.address:
                break
            yield entry
