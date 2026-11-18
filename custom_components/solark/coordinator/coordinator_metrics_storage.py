"""Persistent storage for SolArk metrics.

Provides a lightweight wrapper around Home Assistant's storage helper to
load and save coordinator metrics on a per-config-entry basis. Data is
restored at startup and updated as runtime metrics change.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.storage import Store

if TYPE_CHECKING:
    from ..data import SolArkData

STORAGE_VERSION = 1
STORAGE_KEY = "solark_modbus.metrics"


class MetricsStorage:
    """Handle persistence of coordinator metrics for a config entry.

    This class provides a thin abstraction over Home Assistant's storage helper
    to load and save metrics associated with a specific config entry. Data is
    stored per-entry using a namespaced storage key.
    """

    def __init__(self, runtime_data: SolArkData) -> None:
        """Initialize storage for the config entry stored in the runtime context."""
        self.runtime_data = runtime_data

        self._store = Store(
            runtime_data.hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}.{runtime_data.config_entry.entry_id}",
        )

    # -------------------------
    # internal helpers
    # -------------------------
    @property
    def entry_id(self) -> str:
        """Return the config entry id."""
        return self.runtime_data.config_entry.entry_id

    # -------------------------
    # high-level convenience API
    # -------------------------
    async def async_restore_into_runtime(self) -> None:
        """Load stored metrics and apply them to the runtime object.

        If stored data exists, it is deserialized into the coordinator metrics
        instance. If no data is present, no changes are made.
        """
        metrics = self.runtime_data.coordinator_metrics

        stored: dict | None = await self._store.async_load()
        if stored:
            metrics.from_dict(stored)

    async def async_persist_runtime(self) -> None:
        """Persist current runtime metrics to storage.

        Serializes the coordinator metrics and writes the
        result to Home Assistant storage.
        """
        metrics = self.runtime_data.coordinator_metrics
        await self._store.async_save(metrics.to_dict())
