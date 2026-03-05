import voluptuous as vol
from homeassistant import config_entries

from .const import DEFAULT_BAUDRATE, DEFAULT_TCP_HOST, DEFAULT_TCP_PORT, DEFAULT_DEVICE_ID, DOMAIN


class RTUTCPBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for RTU→TCP Bridge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step when the user adds the integration from the UI."""
        if user_input is not None:
            return self.async_create_entry(title="RTU→TCP Bridge", data=user_input)

        # Show the form with only TCP/baud/device fields
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("baudrate", default=DEFAULT_BAUDRATE): int,
                vol.Optional("tcp_host", default=DEFAULT_TCP_HOST): str,
                vol.Optional("tcp_port", default=DEFAULT_TCP_PORT): int,
                vol.Optional("device_id", default=DEFAULT_DEVICE_ID): int,
            })
        )