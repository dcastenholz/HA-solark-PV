from urllib.parse import urlparse

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback
import voluptuous as vol

from .const import DEFAULT_NAME, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN

@callback
def solark_modbus_entries(hass: HomeAssistant):
    """Return the hosts already configured."""
    return {
        entry.data[CONF_HOST] for entry in hass.config_entries.async_entries(DOMAIN)
    }

def host_valid(netloc):
    
    parsed=urlparse(f'//{netloc}')
    
    try:
        #If it not a URL it might be a serial port.
        if (parsed.port is None) and ((parsed.hostname is None) or (parsed.hostname[0:3] == "com" )):
            return True
            
    #Hostname made no sense.  Error return
    except:
        return False

    return True            

class SolArkModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """SolArk Modbus configflow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def _host_in_configuration_exists(self, host) -> bool:
        """Return True if host exists in configuration."""
        if host in solark_modbus_entries(self.hass):
            return True
        return False

    def _get_data_schema(self, name, host, scan_interval):
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default = name): str,
                vol.Required(CONF_HOST, default = host): str,
                vol.Optional(CONF_SCAN_INTERVAL, default = scan_interval): int
            }
        )

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            if self._host_in_configuration_exists(host):
                errors[CONF_HOST] = "Host already configured"
            elif not host_valid(host):
                errors[CONF_HOST] = "Invalid host IP"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema = self._get_data_schema(DEFAULT_NAME, DEFAULT_HOST, DEFAULT_SCAN_INTERVAL),
            errors=errors
        )

    async def async_step_reconfigure(self, user_input=None) -> ConfigFlowResult:
        errors = {}

        if user_input is not None:
            """await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_mismatch()"""

            """
            user_input[CONF_SCAN_INTERVAL] = 44
            """
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input
            )

        existing_entry = self._get_reconfigure_entry()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema = self._get_data_schema(
                existing_entry.data[CONF_NAME],
                existing_entry.data[CONF_HOST],
                existing_entry.data[CONF_SCAN_INTERVAL]
                ),
            errors=errors
        )