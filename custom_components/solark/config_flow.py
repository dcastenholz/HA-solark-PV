from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback
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

from .config import (
    MAX_DEVICE_ID,
    MAX_PORT_NUMBER,
    MIN_DEVICE_ID,
    MIN_PORT,
    ConnectionType,
    SolArkConfig,
    is_valid_device_id,
    is_valid_rtu_port,
    is_valid_tcp_host,
    is_valid_tcp_port,
)
from .const import (
    DEFAULT_DEVICE_ID,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_PORT_RTU,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL_SECONDS,
)

CONF_CONNECTION_TYPE = "connection_type"
CONNECTION_TCP = ConnectionType.TCP.value
CONNECTION_RTU = ConnectionType.RTU.value

CONF_TCP_HOST = "tcp_host"
CONF_TCP_PORT = "tcp_port"
CONF_RTU_PORT = "rtu_port"
CONF_DEVICE_ID = "device_id"


# ------------------------------------------------------------
# Flow State
# ------------------------------------------------------------

@dataclass
class FlowState:
    name: str = DEFAULT_NAME
    scan_interval: int = DEFAULT_SCAN_INTERVAL
    connection_type: Literal["tcp", "rtu"] = CONNECTION_TCP
    tcp_host: str = DEFAULT_HOST
    tcp_port: int = DEFAULT_PORT
    rtu_port: str = DEFAULT_PORT_RTU
    device_id: int = DEFAULT_DEVICE_ID


# ------------------------------------------------------------
# Config Flow
# ------------------------------------------------------------

class SolArkConfigFlow(ConfigFlow, domain=DOMAIN):
    """SolArk Modbus config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self.state = FlowState()
        # Prevent overwriting user input when reconfiguring: load entry data only once
        self._reconfigure_loaded = False

    # ------------------------------------------------------------
    # Schemas
    # ------------------------------------------------------------

    def _user_schema(self, readonly_name: bool) -> vol.Schema:
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

    def _tcp_schema(self) -> vol.Schema:
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

    def _rtu_schema(self) -> vol.Schema:
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

    # ------------------------------------------------------------
    # Step: user
    # ------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:

        errors: dict[str, str] = {}
        readonly_name = self.context.get("source") == "reconfigure"

        if user_input is not None:
            name = user_input[CONF_NAME]
            existing = solark_modbus_entry_names(self.hass)

            if readonly_name:
                entry = self._get_reconfigure_entry()
                entry_name = entry.data.get(CONF_NAME)
                if isinstance(entry_name, str):
                    existing.discard(entry_name)

            if name in existing:
                errors[CONF_NAME] = "name_already_configured"

            if not errors:
                self.state.name = name
                self.state.scan_interval = user_input[CONF_SCAN_INTERVAL]
                self.state.connection_type = user_input[CONF_CONNECTION_TYPE]

                if self.state.connection_type == CONNECTION_TCP:
                    return await self.async_step_tcp()
                return await self.async_step_rtu()

        return self.async_show_form(
            step_id="user",
            data_schema=self._user_schema(readonly_name),
            errors=errors,
        )

    # ------------------------------------------------------------
    # Step: TCP
    # ------------------------------------------------------------

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:

        errors: dict[str, str] = {}

        if user_input is not None:
            # TCP Host
            if not is_valid_tcp_host(user_input[CONF_TCP_HOST]):
                errors[CONF_TCP_HOST] = "invalid_tcp_host"

            # TCP Port
            try:
                tcp_port = int(user_input[CONF_TCP_PORT])
            except (ValueError, TypeError):
                errors[CONF_TCP_PORT] = "non_int_tcp_port"

            if not is_valid_tcp_port(tcp_port):
                errors[CONF_TCP_PORT] = "invalid_tcp_port"

            # Device ID
            try:
                device_id = int(user_input[CONF_DEVICE_ID])
            except (ValueError, TypeError):
                errors[CONF_DEVICE_ID] = "non_int_device_id"

            if not is_valid_device_id(device_id):
                errors[CONF_DEVICE_ID] = "device_id_out_of_range"

            if not errors:
                self.state.tcp_host = user_input[CONF_TCP_HOST]
                self.state.tcp_port = tcp_port
                self.state.device_id = device_id

                return self._finish_flow()

        return self.async_show_form(
            step_id="tcp",
            data_schema=self._tcp_schema(),
            errors=errors,
            last_step=True,
        )

    # ------------------------------------------------------------
    # Step: RTU
    # ------------------------------------------------------------

    async def async_step_rtu(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:

        errors: dict[str, str] = {}

        if user_input is not None:
            # RTU Port
            if not is_valid_rtu_port(user_input[CONF_RTU_PORT]):
                errors[CONF_RTU_PORT] = "invalid_rtu_port"

            # Device ID
            try:
                device_id = int(user_input[CONF_DEVICE_ID])
            except (ValueError, TypeError):
                errors[CONF_DEVICE_ID] = "non_int_device_id"

            if not is_valid_device_id(device_id):
                errors[CONF_DEVICE_ID] = "device_id_out_of_range"

            if not errors:
                self.state.rtu_port = user_input[CONF_RTU_PORT]
                self.state.device_id = device_id

                return self._finish_flow()

        return self.async_show_form(
            step_id="rtu",
            data_schema=self._rtu_schema(),
            errors=errors,
            last_step=True,
        )

    # ------------------------------------------------------------
    # Reconfigure
    # ------------------------------------------------------------

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:

        entry = self._get_reconfigure_entry()

        if not self._reconfigure_loaded:
            cfg = SolArkConfig(entry)
            self._reconfigure_loaded = True

            self.state.name = entry.data.get(CONF_NAME, DEFAULT_NAME)
            self.state.scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            self.state.device_id = cfg.device_id

            if cfg.connection_type == ConnectionType.TCP:
                self.state.connection_type = CONNECTION_TCP
                self.state.tcp_host = cfg.host or DEFAULT_HOST
                self.state.tcp_port = cfg.port
            else:
                self.state.connection_type = CONNECTION_RTU
                self.state.rtu_port = cfg.serial_port or DEFAULT_PORT_RTU

        return await self.async_step_user(user_input)

    # ------------------------------------------------------------
    # Finish flow
    # ------------------------------------------------------------

    @callback
    def _build_host_string(self) -> str:
        """Return the canonical host string for the entry."""
        if self.state.connection_type == CONNECTION_TCP:
            return f"{self.state.tcp_host}:{self.state.tcp_port}/;{self.state.device_id}"
        return f"{self.state.rtu_port}/;{self.state.device_id}"

    @callback
    def _finish_flow(self) -> ConfigFlowResult:
        data = {
            CONF_NAME: self.state.name,
            CONF_HOST: self._build_host_string(),
            CONF_SCAN_INTERVAL: self.state.scan_interval,
        }

        if self.context.get("source") == "reconfigure":
            entry = self._get_reconfigure_entry()
            self.hass.config_entries.async_update_entry(entry, data=data)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_create_entry(title=self.state.name, data=data)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

@callback
def solark_modbus_entry_names(hass: HomeAssistant) -> set[str]:
    """Return names already configured."""
    names: set[str] = set()
    for entry in hass.config_entries.async_entries(DOMAIN):
        name = entry.data.get(CONF_NAME)
        if isinstance(name, str):
            names.add(name)
    return names