from homeassistant.helpers import device_registry as dr

from .const import DOMAIN


@staticmethod
def update_device_serial(hass, unique_id: str, serial_number: str):
    """Update the serial number of a device in the registry."""
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device({(DOMAIN, unique_id)}, set())
    if device_entry:
        device_registry.async_update_device(
            device_id=device_entry.id,
            serial_number=serial_number
        )

@staticmethod
def update_device_firmware(hass, unique_id: str, firmware: str):
    """Update the sw_version of a device in the registry."""
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device({(DOMAIN, unique_id)}, set())
    if device_entry:
        device_registry.async_update_device(
            device_id=device_entry.id,
            sw_version=firmware
        )
