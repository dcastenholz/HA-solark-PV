"""The SolArk Modbus Integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .config_entry import SolArkConfigEntry
from .coordinator import SolArkCoordinator
from .data import SolArkData

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    entry = SolArkConfigEntry(hass, entry)

    runtime_data = SolArkData(hass, entry)

    coordinator = SolArkCoordinator(runtime_data)
    runtime_data.coordinator = coordinator

    entry.runtime_data = runtime_data

    # Make sure the first data read completes before adding entities. This prevents empty/None data
    await coordinator.async_config_entry_first_refresh()

    # Forward to the normal sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SolArk Modbus entry."""
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    entry = SolArkConfigEntry(hass, entry)

    runtime_data = entry.runtime_data

    # Unload all the sensor entities
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if not unload_ok:
        return False

    # Shutdown resources encapsulated in SolArkData
    await runtime_data.close()
    entry.runtime_data = None

    _LOGGER.debug("SolArk hub '%s' unloaded cleanly", runtime_data.name)
    return True
