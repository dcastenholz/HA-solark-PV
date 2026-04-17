from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .data import SolArkData


class SolArkDeviceInfo:

    @staticmethod
    def _update_device(runtime_data: SolArkData, **kwargs) -> None:
        device_registry = dr.async_get(runtime_data.hass)
        device_entry = device_registry.async_get_device({(DOMAIN, runtime_data.name)}, set(),)

        if device_entry:
            device_registry.async_update_device(
                device_id=device_entry.id,
                **kwargs,
            )

    @staticmethod
    def set_serial_number(runtime_data: SolArkData, serial_number: str) -> None:
        """Update the serial number of a device in the registry."""
        SolArkDeviceInfo._update_device(runtime_data, serial_number=serial_number)

    @staticmethod
    def set_firmware_versions(runtime_data: SolArkData, firmware_versions: str) -> None:
        """Update the sw_version of a device in the registry."""
        SolArkDeviceInfo._update_device(runtime_data, sw_version=firmware_versions)
