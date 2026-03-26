"""Config flow."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import CONN_CLASS_LOCAL_POLL, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback

from .config_flow_state import CONF_CONNECTION_TYPE, ConfigFlowState
from .config_schema import SolArkConfigSchema
from .const import (
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_PORT_RTU,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .modbus_config import (
    ConnectionType,
    is_valid_device_id,
    is_valid_rtu_port,
    is_valid_tcp_host,
    is_valid_tcp_port,
)

CONF_TCP_HOST = "tcp_host"
CONF_TCP_PORT = "tcp_port"
CONF_RTU_PORT = "rtu_port"
CONF_DEVICE_ID = "device_id"


# ------------------------------------------------------------
# Config Flow
# ------------------------------------------------------------

class SolArkConfigFlow(ConfigFlow, domain=DOMAIN):
    """SolArk Modbus config flow."""

    # This is the version number for the config_entry as stored in the config_entries storage
    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL
    is_reconfiguration: bool = False

    def __init__(self) -> None:
        self._state = ConfigFlowState()
        self._schema = SolArkConfigSchema(self._state)
        # Prevent overwriting user input when reconfiguring: load entry data only once
        self._reconfigure_loaded = False

    def is_matching(self, other_flow: ConfigFlow) -> bool:
        return (
            isinstance(other_flow, SolArkConfigFlow)
            and self.context.get("name") is not None
            and self.context.get("name") == other_flow.context.get("name")
        )

    # ------------------------------------------------------------
    # Step: user
    # ------------------------------------------------------------

    async def async_step_user(self, user_input=None):

        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME]
            existing = existing_config_entry_names(self.hass)

            #await self.async_set_unique_id(name)

            # if self.is_reconfiguration:
            #     entry = self._get_reconfigure_entry()
            #     entry_name = entry.data.get(CONF_NAME)
            #     if isinstance(entry_name, str):
            #         existing.discard(entry_name)
            # else:
            #     self._abort_if_unique_id_configured()

            if (not self.is_reconfiguration) and name in existing:
                errors[CONF_NAME] = "name_already_configured"

            if not errors:
                self._state.name = name
                self._state.scan_interval = user_input[CONF_SCAN_INTERVAL]
                self._state.connection_type = user_input[CONF_CONNECTION_TYPE]

                if self._state.connection_type == ConnectionType.TCP:
                    return await self.async_step_tcp()
                return await self.async_step_rtu()

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema.get_user_schema(self.is_reconfiguration),
            errors=errors,
        )

    # ------------------------------------------------------------
    # Step: TCP
    # ------------------------------------------------------------

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Second dialog for TCP."""

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
                self._state.tcp_host = user_input[CONF_TCP_HOST]
                self._state.tcp_port = tcp_port
                self._state.device_id = device_id

                return self._finish_flow()

        return self.async_show_form(
            step_id="tcp",
            data_schema=self._schema.get_tcp_schema(),
            errors=errors,
            last_step=True,
        )

    # ------------------------------------------------------------
    # Step: RTU
    # ------------------------------------------------------------

    async def async_step_rtu(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Second dialog for RTU."""

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
                self._state.rtu_port = user_input[CONF_RTU_PORT]
                self._state.device_id = device_id

                return self._finish_flow()

        return self.async_show_form(
            step_id="rtu",
            data_schema=self._schema.get_rtu_schema(),
            errors=errors,
            last_step=True,
        )

    # ------------------------------------------------------------
    # Reconfigure
    # ------------------------------------------------------------

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:

        self.is_reconfiguration = True
        entry = self._get_reconfigure_entry()

        if not self._reconfigure_loaded:
            state: ConfigFlowState = ConfigFlowState.from_config_entry(entry)
            self._reconfigure_loaded = True

            self._state.name = entry.data.get(CONF_NAME, DEFAULT_NAME)
            self._state.scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            self._state.device_id = state.device_id

            if state.connection_type == ConnectionType.TCP:
                self._state.connection_type = ConnectionType.TCP
                self._state.tcp_host = state.tcp_host or DEFAULT_HOST
                self._state.tcp_port = state.tcp_port
            else:
                self._state.connection_type = ConnectionType.RTU
                self._state.rtu_port = state.rtu_port or DEFAULT_PORT_RTU

        return await self.async_step_user(user_input)

    # ------------------------------------------------------------
    # Finish flow
    # ------------------------------------------------------------

    @callback
    def _finish_flow(self) -> ConfigFlowResult:
        data: dict[str, Any] = self._state.get_config_entry_data()

        if self.context.get("source") == "reconfigure":
            entry = self._get_reconfigure_entry()
            return self.async_update_reload_and_abort(entry, data=data, reason="reconfigure_successful")

        return self.async_create_entry(title=self._state.name, data=data)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

@callback
def existing_config_entry_names(hass: HomeAssistant) -> set[str]:
    """Return names already configured."""
    names: set[str] = set()
    for entry in hass.config_entries.async_entries(DOMAIN):
        name: str = entry.data[CONF_NAME]
        if isinstance(name, str):
            names.add(name)
    return names
