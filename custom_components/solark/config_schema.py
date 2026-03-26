"""Configuration schema."""

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

from .config_flow_state import ConfigFlowState
from .const import (
    MIN_DEVICE_ID,
    MIN_PORT,
    MIN_SCAN_INTERVAL_SECONDS,
)
from .modbus_config import (
    MAX_DEVICE_ID,
    MAX_PORT_NUMBER,
    ConnectionType,
)

CONF_CONNECTION_TYPE = "connection_type"
CONNECTION_TCP = ConnectionType.TCP.value
CONNECTION_RTU = ConnectionType.RTU.value

CONF_TCP_HOST = "tcp_host"
CONF_TCP_PORT = "tcp_port"
CONF_RTU_PORT = "rtu_port"
CONF_DEVICE_ID = "device_id"


# ------------------------------------------------------------
# Config schema
# ------------------------------------------------------------

class SolArkConfigSchema:
    state: ConfigFlowState

    def __init__(self, state: ConfigFlowState):
        self.state = state

    # ------------------------------------------------------------
    # Schemas
    # ------------------------------------------------------------

    def get_user_schema(self, readonly_name: bool) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default=self.state.name): TextSelector(
                    TextSelectorConfig(read_only=readonly_name)
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=self.state.scan_interval
                ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL_SECONDS)),
                vol.Required(
                    CONF_CONNECTION_TYPE, default=self.state.connection_type
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
        return vol.Schema(
            {
                vol.Required(CONF_TCP_HOST, default=self.state.tcp_host): str,
                vol.Required(CONF_TCP_PORT, default=self.state.tcp_port): vol.All(
                    int,
                    vol.Range(min=1, max=MAX_PORT_NUMBER),
                    NumberSelector(
                        NumberSelectorConfig(min=MIN_PORT, max=MAX_PORT_NUMBER, step=1, mode=NumberSelectorMode.BOX)
                    )
                ),
                vol.Required(CONF_DEVICE_ID, default=self.state.device_id): vol.All(
                    int,
                    vol.Range(min=1, max=MAX_DEVICE_ID),NumberSelector(
                        NumberSelectorConfig(min=MIN_DEVICE_ID, max=MAX_DEVICE_ID, step=1, mode=NumberSelectorMode.BOX)
                    )
                ),
            }
        )

    def get_rtu_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_RTU_PORT, default=self.state.rtu_port): str,
                vol.Required(CONF_DEVICE_ID, default=self.state.device_id): vol.All(
                    int,
                    vol.Range(min=1, max=MAX_DEVICE_ID),
                    NumberSelector(
                        NumberSelectorConfig(min=MIN_DEVICE_ID, max=MAX_DEVICE_ID, step=1, mode=NumberSelectorMode.BOX)
                    )
                ),
            }
        )
