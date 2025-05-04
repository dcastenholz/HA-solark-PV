"""Handle the Configuration Flow."""

from urllib.parse import urlparse

#
# from config_schema import Get_data_schema
# import ConfigSchema as cs
# import voluptuous as vol
from config.custom_components.solark_modbus_dc.hub import SolArkModbusHub
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback

from . import config_schema
from .const import DEFAULT_HOST, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN


@callback
def solark_modbus_entries(hass: HomeAssistant) -> set[str]:
    """Return the hosts already configured."""
    return {
        entry.data[CONF_HOST] for entry in hass.config_entries.async_entries(DOMAIN)
    }


@callback
def solark_modbus_entry_ids(hass: HomeAssistant) -> set[str]:
    """Return the hosts already configured."""
    return {entry.entry_id for entry in hass.config_entries.async_entries(DOMAIN)}


@callback
def solark_modbus_entry_ids_by_name(hass: HomeAssistant, name: str) -> set[str]:
    """Return the hosts already configured."""
    return {
        entry.entry_id
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.data[CONF_NAME] == name
    }


@callback
def solark_modbus_entry_name_by_entry_id(
    hass: HomeAssistant, entry_id: str
) -> set[str]:
    """Return the hosts already configured."""
    # ret: set[str]
    entries: dict[str, dict[str, SolArkModbusHub]]
    entries = hass.data[DOMAIN].items()
    # entry: SolArkModbusHub
    hub_entry: dict[str, SolArkModbusHub]
    hub: SolArkModbusHub
    for name, hub_entry in entries:
        # hub_name = next(iter(hub_entry))
        hub = hub_entry["hub"]
        if hub.config_entry.entry_id == entry_id:
            ret = name
            break
    return ret


def host_valid(netloc):
    """Check to see if the inputted hostname is valid."""
    parsed = urlparse(f"//{netloc}")

    try:
        # If it not a URL it might be a serial port.
        if (parsed.port is None) and (
            (parsed.hostname is None) or (parsed.hostname[0:3] == "com")
        ):
            return True

    # Hostname made no sense.  Error return
    except:  # noqa: E722
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

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            if self._host_in_configuration_exists(host):
                # TODO - Move strings
                errors[CONF_HOST] = "Host already configured"
            elif not host_valid(host):
                # TODO - Move strings
                errors[CONF_HOST] = "Invalid host IP"
            else:
                # Disallow creation of another device with a host used by an existing device
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=config_schema.get_schema(
                DEFAULT_NAME, DEFAULT_HOST, DEFAULT_SCAN_INTERVAL
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None) -> ConfigFlowResult:
        """Handle the reconfiguration step."""
        errors = {}

        if user_input is not None:
            existing_entry_data = solark_config_entry_data(self.hass)
            all_entries = self.hass.config_entries.async_entries(DOMAIN)

            name = user_input[CONF_NAME]
            old_name = self._get_reconfigure_entry().data[CONF_NAME]

            entries_with_name = solark_modbus_entry_ids_by_name(self.hass, name)

            if len(entries_with_name) > 0 and (
                len(entries_with_name) == 1
                and self._reconfigure_entry_id not in entries_with_name
            ):
                errors[CONF_HOST] = "already_configured"

            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(), data_updates=user_input
            )

        existing_entry = self._get_reconfigure_entry()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=config_schema.get_schema(
                existing_entry.data[CONF_NAME],
                existing_entry.data[CONF_HOST],
                existing_entry.data[CONF_SCAN_INTERVAL],
            ),
            errors=errors,
        )


@callback
def solark_config_entry_data(hass: HomeAssistant) -> set[str, str, str]:
    """Return the hosts already configured."""
    return {
        (entry.entry_id, entry.data[CONF_NAME], entry.data[CONF_HOST])
        for entry in hass.config_entries.async_entries(DOMAIN)
    }
