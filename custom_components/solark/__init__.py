"""The SolArk Modbus Integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
from .config.config_versions import ConfigVersions
from .coordinator.coordinator import SolArkCoordinator
from .data import SolArkData
from .helpers.base_entry_list import BaseEntryList

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

# TODO - Complete version logic and delete this
ALLOW_VERSION_UPDATE: bool = False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load configuration entry."""
    runtime_data = SolArkData(hass, entry)

    coordinator = SolArkCoordinator(runtime_data)
    runtime_data.coordinator = coordinator

    await runtime_data.on_load_entry()

    entry.runtime_data = runtime_data

    # Make sure the first data read completes before adding entities. This prevents empty/None data
    await coordinator.async_config_entry_first_refresh()

    # Set the configured entities to be enabled by default
    BaseEntryList.set_config_enabled_by_default(entry)
    BaseEntryList.set_map_enabled_by_default(runtime_data.metrics_map)

    # Forward to the normal sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload configuration entry."""

    runtime_data: SolArkData = entry.runtime_data

    # Save coordinator metrics
    await runtime_data.store_metrics()

    # Unload all the sensor entities
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if not unload_ok:
        # TODO - Is this correct???
        return False

    # Shutdown resources encapsulated in SolArkData
    await runtime_data.on_unload_entry()
    entry.runtime_data = None

    _LOGGER.debug("SolArk hub '%s' unloaded cleanly", runtime_data.name)
    return True

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate configuration entry from older version to new version."""

    if not ALLOW_VERSION_UPDATE:
        return True

    await ConfigVersions.migrate(hass, entry)

    return True
