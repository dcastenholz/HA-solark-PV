from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry

from ._dev_options import DevOptions_ConfigData_DebugValues
from .config_connection_type import ConnectionType
from .config_versions import ConfigVersions
from .const import (
    DEFAULT_DEVICE_ID,
    DEFAULT_HOST,
    DEFAULT_MAX_STALE_DATA_AGE_SECONDS,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_PORT_RTU,
    DEFAULT_SCAN_INTERVAL,
)


# ------------------------------------------------------------
# Config Data
# ------------------------------------------------------------
@dataclass
class ConfigData:
    name: str = DEFAULT_NAME
    scan_interval: int = DEFAULT_SCAN_INTERVAL
    max_stale_data_age_seconds: int = DEFAULT_MAX_STALE_DATA_AGE_SECONDS
    connection_type: ConnectionType = ConnectionType.TCP
    tcp_host: str = DEFAULT_HOST
    tcp_port: int = DEFAULT_PORT
    rtu_port: str = DEFAULT_PORT_RTU
    device_id: int = DEFAULT_DEVICE_ID

    @staticmethod
    def from_storage_data(entry: ConfigEntry) ->  ConfigData:
        if entry.version == 1:
            config_data: ConfigData = ConfigData()
            ConfigVersions.from_storage_data_v1(config_data, entry.data)

            # Modify if set to use test values
            DevOptions_ConfigData_DebugValues.modify_config_data_with_debug_values_v1(config_data)

            return config_data
        else:
            raise ValueError(entry.version)

    def to_storage_data(self, version: int) -> dict[str, Any]:
        if version == 1:
            return ConfigVersions.to_storage_data_v1(self)
        else:
            raise ValueError(version)
