import logging
from collections import defaultdict
from typing import Callable

from .base_map_entry import BaseMapEntry
from .data import SolArkData
from .register_value_types import SensorValue

_LOGGER = logging.getLogger(__name__)

Listener = Callable[[SensorValue, SensorValue], None]


# TODO - If this is only used by a small static set of keys, simplify!!!
class DataChangeDispatcher:
    """Compares two dict snapshots and triggers per-key listeners."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Listener]] = defaultdict(list)

    def register(self, entry: BaseMapEntry, callback: Listener) -> None:
        key = entry.key
        if callback not in self._listeners[key]:
            self._listeners[key].append(callback)

    def unregister(self, key: str, callback: Listener) -> None:
        listeners = self._listeners.get(key)
        if listeners and callback in listeners:
            listeners.remove(callback)

    def clear(self) -> None:
        """Remove all listeners (used on shutdown)."""
        self._listeners.clear()

    def handle_changes(self, runtime_data: SolArkData) -> None:
        """Compare dicts and call listeners for changed keys.
        The fist data update will trigger the change handler for
        all values that are registered for listening."""

        curr = runtime_data.last_data_updated

        if curr is None:
            return

        curr_data: dict[str, SensorValue] = curr.data

        prev = runtime_data.previous_data_updated
        prev_data: dict[str, SensorValue] = prev.data if prev else {}

        for key in set(prev_data) | set(curr_data):
            listener = self._listeners.get(key)
            if not listener:
                continue

            old_value = prev_data.get(key)
            new_value = curr_data.get(key)

            if old_value == new_value:
                continue

            for cb in listener:
                # If one callback fails, log it, but continue with the rest of the list
                try:
                    cb(new_value, old_value)
                except Exception:
                    _LOGGER.exception(
                        "DataChangeDispatcher listener failed: key=%s, callback=%s, old=%r, new=%r",
                        key,
                        getattr(cb, "__qualname__", repr(cb)),
                        old_value,
                        new_value,
                    )
