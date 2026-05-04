'''Class to create a sensor for viewing the current configuration properties'''
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL

from .config.config_connection_type import CONF_CONNECTION_TYPE, ConnectionType
from .config.config_data import ConfigData
from .config.config_schema import CONF_MAX_STALE_DATA_AGE_SECONDS


class ConfigSensor:
    '''Class to create a sensor for viewing the current configuration properties'''

    @staticmethod
    def get_data(entry: ConfigEntry) -> dict[str, Any]:
        '''Get a dictionary of the configuration proerty names and values'''
        config_data: ConfigData = ConfigData.from_storage_data(entry)

        data: dict[str, Any] = {
            CONF_NAME: config_data.name,
            CONF_SCAN_INTERVAL: config_data.scan_interval,
            CONF_MAX_STALE_DATA_AGE_SECONDS: config_data.max_stale_data_age_seconds,
            CONF_CONNECTION_TYPE: config_data.connection_type,
        }

        if config_data.connection_type == ConnectionType.TCP:
            data.update(
                {
                    CONF_HOST: config_data.tcp_host,
                    CONF_PORT: config_data.tcp_port
                }
            )
        else:
            data.update(
                {
                    CONF_PORT: config_data.rtu_port
                }
            )
        return data
