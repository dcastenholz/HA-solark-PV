from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntry, DeviceRegistry

from .const import DOMAIN
from .data import SolArkData
from .register_value_types import SensorValue


class SolArkDeviceInfo:

    @staticmethod
    def _get_device_entry(
        runtime_data: SolArkData,
        device_registry: DeviceRegistry,
    ) -> DeviceEntry | None:
        return device_registry.async_get_device(
            {(DOMAIN, runtime_data.name)},
            set(),
        )

    @staticmethod
    def set_serial_number(runtime_data: SolArkData) -> None:
        """Update the serial number of a device in the registry."""
        device_registry = dr.async_get(runtime_data.hass)
        device_entry = SolArkDeviceInfo._get_device_entry(runtime_data, device_registry)

        sensor_value: SensorValue = runtime_data.register_map.SN.sensor_value

        if device_entry and isinstance(sensor_value, str):
            device_registry.async_update_device(
                device_id=device_entry.id,
                serial_number=sensor_value,
            )

    @staticmethod
    def set_firmware_versions(runtime_data: SolArkData) -> None:
        """Update the sw_version of a device in the registry."""
        device_registry = dr.async_get(runtime_data.hass)
        device_entry = SolArkDeviceInfo._get_device_entry(runtime_data, device_registry)

        sensor_value: SensorValue = runtime_data.calculated_sensor_map.FIRMWARE.sensor_value

        if device_entry and isinstance(sensor_value, str):
            device_registry.async_update_device(
                device_id=device_entry.id,
                sw_version=sensor_value,
            )