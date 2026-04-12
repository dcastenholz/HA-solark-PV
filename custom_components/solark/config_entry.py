from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from .const import DOMAIN

if TYPE_CHECKING:
    from .data import SolArkData

class SolArkConfigEntry(ConfigEntry):
    """ConfigEntry wrapper with cross-version runtime_data support.
       This class can be removed if manifest.json has "homeassistant": "2024.6.0" or greater."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass
        self._entry = entry
        self._has_native_runtime_data = hasattr(ConfigEntry, "runtime_data")

    #
    # Proxy attributes to the underlying ConfigEntry
    #
    def __getattr__(self, name: str) -> Any:
        return getattr(self._entry, name)

    #
    # Runtime data abstraction
    #
    @property
    def runtime_data(self) -> "SolArkData":
        """Return runtime data regardless of HA version."""
        if self._has_native_runtime_data:
            return self._entry.runtime_data

        data = self._hass.data.get(DOMAIN, {}).get(self._entry.entry_id)
        if data is None:
            raise RuntimeError("runtime_data not initialized")
        return data

    @runtime_data.setter
    def runtime_data(self, value: "SolArkData | None") -> None:
        """Store runtime data regardless of HA version."""
        if self._has_native_runtime_data:
            self._entry.runtime_data = value
            return

        domain_store = self._hass.data.setdefault(DOMAIN, {})

        if value is None:
            domain_store.pop(self._entry.entry_id, None)
        else:
            domain_store[self._entry.entry_id] = value

    @property
    def name(self: ConfigEntry) -> str:
        return self.data[CONF_NAME]

    @property
    def scan_interval(self: ConfigEntry) -> int:
        return self.data[CONF_SCAN_INTERVAL]
