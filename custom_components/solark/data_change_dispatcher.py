from collections import defaultdict
from typing import Any, Callable
import logging
from .data import SolArkData

_LOGGER = logging.getLogger(__name__)

Listener = Callable[[Any, Any], None]


class DataChangeDispatcher:
    """Compares two dict snapshots and triggers per-key listeners."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Listener]] = defaultdict(list)

    def register(self, key: str, callback: Listener) -> None:
        if callback not in self._listeners[key]:
            self._listeners[key].append(callback)

    def unregister(self, key: str, callback: Listener) -> None:
        if callback in self._listeners.get(key, []):
            self._listeners[key].remove(callback)

    def _dispatch(self, old: dict[str, Any] | None, new: dict[str, Any]) -> None:
        """Compare dicts and call listeners for changed keys."""
        old = old or {}

        for key in set(old) | set(new):
            old_value = old.get(key)
            new_value = new.get(key)

            if old_value != new_value:
                for cb in list(self._listeners.get(key, [])):
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

    def dispatch(self, runtime_data: SolArkData) -> None:
        """Compare dicts and call listeners for changed keys."""
        prev = runtime_data.previous_data_updated
        curr = runtime_data.last_data_updated

        if curr is None:
            return

        curr_data = curr.data
        prev_data = None if prev is None else prev.data

        self._dispatch(prev_data, curr_data)
