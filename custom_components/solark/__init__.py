"""The SolArk Modbus Integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .base_map_list import BaseMapEntryList

# This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
from .config_entry import SolArkConfigEntry
from .config_versions import ConfigVersions
from .coordinator import SolArkCoordinator
from .data import SolArkData

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# TODO - Complete version logic and delete this
ALLOW_VERSION_UPDATE: bool = False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    entry = SolArkConfigEntry(hass, entry)

    runtime_data = SolArkData(hass, entry)

    coordinator = SolArkCoordinator(runtime_data)
    runtime_data.coordinator = coordinator

    entry.runtime_data = runtime_data

    # Make sure the first data read completes before adding entities. This prevents empty/None data
    await coordinator.async_config_entry_first_refresh()

    # Set the configured entities to be enabled by default
    BaseMapEntryList.set_config_enabled_by_default(entry)

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

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entry from older version to new version."""

    if not ALLOW_VERSION_UPDATE:
        return True

    await ConfigVersions.migrate(hass, entry)

    return True
