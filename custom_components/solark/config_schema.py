"""Configuration schema."""

from typing import TYPE_CHECKING, Final

import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .config_connection_type import CONF_CONNECTION_TYPE, CONNECTION_RTU, CONNECTION_TCP
from .const import (
    MAX_DEVICE_ID,
    MAX_PORT_NUMBER,
    MIN_DEVICE_ID,
    MIN_PORT,
    MIN_SCAN_INTERVAL_SECONDS,
)

if TYPE_CHECKING:
    from .config_data import ConfigData


CONF_TCP_HOST = "tcp_host"
CONF_TCP_PORT = "tcp_port"
CONF_RTU_PORT = "rtu_port"
CONF_DEVICE_ID = "device_id"
CONF_MAX_STALE_DATA_AGE_SECONDS: Final = "max_stale_data_age_seconds"

# ------------------------------------------------------------
# Config schema
# ------------------------------------------------------------

class SolArkConfigSchema:
    '''Class that defines the schema for the config and reconfig flows.'''
    config_data: "ConfigData"

    def __init__(self, config_data: "ConfigData"):
        self.config_data = config_data

    # ------------------------------------------------------------
    # Schemas
    # ------------------------------------------------------------

    def get_user_schema(self, readonly_name: bool) -> vol.Schema:
        '''Returns the common base config schema, including the connection type.'''
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default=self.config_data.name): TextSelector(
                    TextSelectorConfig(read_only=readonly_name)
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=self.config_data.scan_interval
                ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL_SECONDS)),
                vol.Required(
                    CONF_MAX_STALE_DATA_AGE_SECONDS, default=self.config_data.max_stale_data_age_seconds
                ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL_SECONDS)),
                vol.Required(
                    CONF_CONNECTION_TYPE, default=self.config_data.connection_type
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": CONNECTION_TCP, "label": "TCP"},
                            {"value": CONNECTION_RTU, "label": "RTU"},
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

    def get_tcp_schema(self) -> vol.Schema:
        '''Returns the tcp config schema based on the chosen connection type.'''
        return vol.Schema(
            {
                vol.Required(CONF_TCP_HOST, default=self.config_data.tcp_host): str,
                vol.Required(CONF_TCP_PORT, default=self.config_data.tcp_port): vol.All(
                    int,
                    vol.Range(min=1, max=MAX_PORT_NUMBER),
                    NumberSelector(
                        NumberSelectorConfig(min=MIN_PORT, max=MAX_PORT_NUMBER, step=1, mode=NumberSelectorMode.BOX)
                    )
                ),
                vol.Required(CONF_DEVICE_ID, default=self.config_data.device_id): vol.All(
                    int,
                    vol.Range(min=1, max=MAX_DEVICE_ID),NumberSelector(
                        NumberSelectorConfig(min=MIN_DEVICE_ID, max=MAX_DEVICE_ID, step=1, mode=NumberSelectorMode.BOX)
                    )
                ),
            }
        )

    def get_rtu_schema(self) -> vol.Schema:
        '''Returns the rtu config schema based on the chosen connection type.'''
        return vol.Schema(
            {
                vol.Required(CONF_RTU_PORT, default=self.config_data.rtu_port): str,
                vol.Required(CONF_DEVICE_ID, default=self.config_data.device_id): vol.All(
                    int,
                    vol.Range(min=1, max=MAX_DEVICE_ID),
                    NumberSelector(
                        NumberSelectorConfig(min=MIN_DEVICE_ID, max=MAX_DEVICE_ID, step=1, mode=NumberSelectorMode.BOX)
                    )
                ),
            }
        )
