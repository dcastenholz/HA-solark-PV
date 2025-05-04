"""The SolArk Modbus Integration."""

import asyncio
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from . import config_schema
from .config_flow import solark_modbus_entry_name_by_entry_id
from .const import DEFAULT_HOST, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN
from .hub import SolArkModbusHub

_LOGGER = logging.getLogger(__name__)

SOLARK_MODBUS_SCHEMA = config_schema.get_schema(
    DEFAULT_NAME, DEFAULT_HOST, DEFAULT_SCAN_INTERVAL
)


# SOLARK_MODBUS_SCHEMA = vol.Schema(
#    {
#        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
#        vol.Required(CONF_HOST): cv.string,
#        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
#    }
# )

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: SOLARK_MODBUS_SCHEMA})}, extra=vol.ALLOW_EXTRA
)

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config):
    """Set up the SolArk modbus component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a SolArk modbus."""
    name = entry.data[CONF_NAME]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]
    host = entry.data[CONF_HOST]

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = SolArkModbusHub(hass, name, host, scan_interval)
    # Register the hub
    hass.data[DOMAIN][name] = {"hub": hub}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload SolArk mobus entry."""
    try:
        unload_ok = all(
            await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, component)
                    for component in PLATFORMS
                ]
            )
        )
        if not unload_ok:
            return False
    except KeyError:
        _LOGGER.debug("Exception %s.%s", DOMAIN, KeyError)

    existing_entry = solark_modbus_entry_name_by_entry_id(hass, entry.entry_id)

    try:
        entries: dict[str, SolArkModbusHub]
        entries = hass.data[DOMAIN]
        entries.pop(existing_entry)
        # _LOGGER.debug("Pop succeeded")

    except KeyError as e:
        _LOGGER.debug("Exception %s.%s", DOMAIN, e.args)
        return False

    return True
