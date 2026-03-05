"""
__init__.py - RTU→TCP Bridge integration for Home Assistant.

Automatically starts the RTU→TCP bridge in a background thread
and logs the PTY path for clients (e.g., SolarK) to connect.
"""

import logging
import threading

from homeassistant.core import HomeAssistant

from .bridge import run_static_test, start_bridge
from .const import DEFAULT_BAUDRATE, DEFAULT_DEVICE_ID, DEFAULT_REG_COUNT, DEFAULT_SERIAL_PORT, DEFAULT_TCP_HOST, DEFAULT_TCP_PORT

_LOGGER = logging.getLogger(__name__)


# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Legacy YAML setup (optional)."""
#     _LOGGER.info("RTU→TCP Bridge loaded via YAML (not recommended).")
#     return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up RTU→TCP Bridge from a UI config entry."""

    # Extract configuration values with defaults
    serial_port = entry.data.get("serial_port", DEFAULT_SERIAL_PORT)
    baudrate = entry.data.get("baudrate", DEFAULT_BAUDRATE)
    tcp_host = entry.data.get("tcp_host", DEFAULT_TCP_HOST)
    tcp_port = entry.data.get("tcp_port", DEFAULT_TCP_PORT)
    device_id = entry.data.get("device_id", DEFAULT_DEVICE_ID)
    reg_count = entry.data.get("reg_count", DEFAULT_REG_COUNT)

    def run_bridge() -> None:
        """Start the bridge in a background thread and log the PTY path."""
        _LOGGER.info("Starting RTU→TCP bridge thread")
        try:
            # Run static test
            run_static_test(tcp_host, tcp_port, device_id)
        except Exception as exc:
            _LOGGER.error("Failed static test: %s", exc)

        try:
            slave_port = start_bridge(
                serial_port=serial_port,
                baudrate=baudrate,
                tcp_host=tcp_host,
                tcp_port=tcp_port,
                device_id=device_id,
                reg_count=reg_count,
            )
            _LOGGER.info("RTU→TCP bridge ready. Connect your RTU client to: %s", slave_port)
        except Exception as exc:
            _LOGGER.error("Failed to start RTU→TCP bridge: %s", exc, exc_info=True)

    thread = threading.Thread(target=run_bridge, daemon=True)
    thread.start()

    return True
