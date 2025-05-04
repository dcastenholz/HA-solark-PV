"""Configuration schema."""

import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv


def get_schema(name: str, host: str, scan_interval: int):
    """Get the full data schema."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=name): cv.string,
            get_reconfig_schema(host, scan_interval): vol.Schema,
        }
    )


def get_reconfig_schema(host: str, scan_interval: int):
    """Get the reconfiguration data schema."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=host): cv.string,
            vol.Required(CONF_SCAN_INTERVAL, default=scan_interval): cv.positive_int,
        }
    )
