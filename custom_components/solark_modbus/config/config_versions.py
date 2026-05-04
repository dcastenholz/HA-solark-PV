"""Configuration version helpers for SolArk."""

from types import MappingProxyType
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry

from ..const import DEFAULT_MAX_STALE_DATA_AGE_SECONDS, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, MAX_DEVICE_ID
from .config_connection_type import CONNECTION_TCP, ConnectionType
from .config_schema import CONF_MAX_STALE_DATA_AGE_SECONDS

if TYPE_CHECKING:
    from .config_data import ConfigData

class ConfigVersions:
    """Helpers for migrating and serializing config entry versions."""

    @staticmethod
    async def migrate(hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Migrate a config entry to the current version."""
        if entry.version == 1:
            await ConfigVersions.migrate_entities_v1_to_v2(hass, entry)


    @staticmethod
    async def migrate_entities_v1_to_v2(hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Migrate entity registry data from version 1 to version 2."""
        registry = entity_registry.async_get(hass)

        for entity in entity_registry.async_entries_for_config_entry(registry, entry.entry_id):
            unique_id = entity.unique_id

            # TODO - validate this!!!
            # Example: rename entity_id
            if unique_id.endswith("_totalgrid_e"):
                new_entity_id = entity.entity_id.replace(
                    "total_grid_breaker_energy", "total_inverter_energy"
                )

                registry.async_update_entity(
                    entity.entity_id,
                    new_entity_id=new_entity_id,
                    name="Total Inverter Energy",
                )

        hass.config_entries.async_update_entry(entry, version=2)

    @staticmethod
    def from_storage_data_v1(config_data: "ConfigData", data: MappingProxyType[str, Any]) -> None:
        """
        Initialize the ConfigData object from a ConfigEntry with a single url stored in entry.data[CONF_HOST].

        The hostname (entry.data[CONF_HOST]) can be a valid URL (e.g. 192.168.2.2) or a serial port name (e.g. /dev/ttyUSB0 or COM1).
        If the hostname is not a valid URL, it will be interpreted as a serial port name.

        The device ID is an optional parameter that can be specified as a query parameter in the hostname (e.g. 192.168.2.2/;3).
        If the device ID is not specified, it will default to 1.

        The connection type is determined based on the hostname. If the hostname is a valid URL, it will be interpreted as a TCP connection.
        If the hostname is a serial port name, it will be interpreted as a serial connection."""
        config_data.name = str(data.get(CONF_NAME))

        parsed = urlparse(f"//{data[CONF_HOST]}")

        # If it not a proper URL it might be a serial port.
        # This logic is tested to work with linux and windows serial port names,
        # port numbers and device_ids
        #
        # Tested URLs:
        #  192.168.2.2
        #  192.268.2.2:502
        #  192.168.2.2:502/;3
        #  192.168.2.2/;3
        #  /dev/ttyUSB0
        #  /dev/ttyUDB0/;3
        #  COM1
        #  COM1/;3
        #

        if (parsed.port is None) and ((parsed.hostname is None) or parsed.hostname.lower().startswith("com")):
            config_data.connection_type = ConnectionType.RTU
            config_data.rtu_port = parsed.path.rstrip("/") + parsed.netloc
        else:
            config_data.connection_type = ConnectionType.TCP
            config_data.tcp_host = str(parsed.hostname)
            config_data.tcp_port = parsed.port or DEFAULT_PORT

        if parsed.params.isdigit() and int(parsed.params) < MAX_DEVICE_ID:
            config_data.device_id = int(parsed.params)

        config_data.scan_interval = data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        config_data.max_stale_data_age_seconds = data.get(CONF_MAX_STALE_DATA_AGE_SECONDS, DEFAULT_MAX_STALE_DATA_AGE_SECONDS)

    @staticmethod
    def to_storage_data_v1(config_data: "ConfigData") -> dict[str, str]:
        """Serialize config data using the version 1 storage format."""
        data: dict[str, Any] = {
            CONF_NAME: config_data.name,
            CONF_SCAN_INTERVAL: config_data.scan_interval,
            CONF_MAX_STALE_DATA_AGE_SECONDS: config_data.max_stale_data_age_seconds,
        }

        # Add the VERSION 1 canonical host string for the entry.
        host_string: str
        if config_data.connection_type == CONNECTION_TCP:
            host_string = f"{config_data.tcp_host}:{config_data.tcp_port}/;{config_data.device_id}"
        else:
            host_string = f"{config_data.rtu_port}/;{config_data.device_id}"

        data.update({CONF_HOST: host_string})

        return data
