"""Device information helpers."""

import logging

from homeassistant.helpers import device_registry as dr

from ..const import DOMAIN
from ..data import SolArkData

_LOGGER = logging.getLogger(__name__)

class SolArkDeviceInfo:
    """Helpers for updating the device registry entry."""

    @staticmethod
    def _update_device(runtime_data: SolArkData, **kwargs) -> None:
        def _do_update():
            device_registry = dr.async_get(runtime_data.hass)

            device_entry = device_registry.async_get_device(
                identifiers={(DOMAIN, runtime_data.name)},
                connections=set(),
            )

            if device_entry:
                device_registry.async_update_device(
                    device_id=device_entry.id,
                    **kwargs,
                )
                _LOGGER.debug("Wrote to device: %s", kwargs)


        runtime_data.hass.loop.call_soon_threadsafe(_do_update)

    @staticmethod
    def handle_serial_number_change(
        runtime_data: SolArkData,
        serial_number: str,
    ) -> None:
        """If changed, update the device serial number."""

        if serial_number == runtime_data.serial_number:
            _LOGGER.debug("Serial Number unchanged.")
            return

        # Save first to prevent duplicate scheduling if re-entered
        runtime_data.serial_number = serial_number

        SolArkDeviceInfo._update_device(runtime_data, serial_number=serial_number)
        _LOGGER.debug("Wrote Serial Number to device.")


    @staticmethod
    def set_serial_number(runtime_data: SolArkData, serial_number: str) -> None:
        """Force update serial number."""
        runtime_data.serial_number = serial_number
        SolArkDeviceInfo._update_device(runtime_data, serial_number=serial_number)

    @staticmethod
    def set_firmware_versions(runtime_data: SolArkData, firmware_versions: str) -> None:
        """Update firmware version."""
        SolArkDeviceInfo._update_device(runtime_data, sw_version=firmware_versions)
