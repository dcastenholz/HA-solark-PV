import logging
from datetime import datetime, timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .calculated_sensors import CalculatedSensors
from .data import SolArkData
from .device_info import update_device_firmware, update_device_serial
from .modbus_client import SolArkModbusClient
from .register_map import RegisterValue
from .solark_register_map import SolArkRegisterMap

_LOGGER = logging.getLogger(__name__)

class SolArkCoordinator(DataUpdateCoordinator[dict]):
    _runtime_data: SolArkData
    _update_cnt: int

    def __init__(self, runtime_data: SolArkData):
        # Register the coordinator with the runtime_data
        self._runtime_data = runtime_data
        self._runtime_data.coordinator = self

        self._update_cnt = 0
        self._last_successful_data: dict[str, RegisterValue] | None = None
        self._last_successful_timestamp: datetime | None = None
        self.max_stale_data_age = 300  # seconds

        name = self._runtime_data.name

        super().__init__(
            runtime_data.hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=runtime_data.scan_interval),
        )

        self.has_inverter_data = False

    # @property
    # def modbus_client(self) -> SolArkModbusClient:
    #     return self._runtime_data.modbus_client

    async def _async_update_data(self) -> dict:
        """Read the data from the inverter and return it as a dictionary."""
        current_data: dict = {}
        register_map: SolArkRegisterMap = self._runtime_data.register_map
        calculated_sensor_map: CalculatedSensors = self._runtime_data.calculated_sensor_map
        modbus_client: SolArkModbusClient = self._runtime_data.modbus_client

        try:

            register_map.init()  # Initialize the register map before reading

            if not self.has_inverter_data:  # Inverter serial number is only fetched once
                await self.hass.async_add_executor_job(modbus_client.read_modbus_inverter_data)

                if not register_map.is_error():
                    if(register_map.SN.register_value is not None):
                        update_device_serial(self.hass, self.name, str(register_map.SN.register_value))
                        self.has_inverter_data = True

                    # if(register_map.FIRMWARE.register_value is not None):
                    #     update_device_firmware(self.hass, self.name, str(register_map.FIRMWARE.register_value))
                    #     self.has_inverter_data = True


            # Read realtime data
            await self.hass.async_add_executor_job(modbus_client.read_modbus_realtime_data)

            # If we already have a read failure, post processing is unnecessary and may fail as well
            if not modbus_client.register_map.is_error():
                await self.hass.async_add_executor_job(calculated_sensor_map.post_process)

            current_data = {**register_map.as_dict(), **calculated_sensor_map.as_dict()}

        except Exception as e:
            _LOGGER.exception("Unexpected error reading inverter data: %s", e)
            current_data = {}

        # Return combined data safely
        return self._handle_stale_data(current_data)

    async def async_stop(self, *_):
        """Stop coordinator updates and close the client."""
        try:
            await self.hass.async_add_executor_job(self._runtime_data.modbus_client.close)
        except Exception as exc:
            _LOGGER.error("Error stopping coordinator: %s", exc, exc_info=True)

    def _handle_stale_data(self, current_data: dict[str, RegisterValue]) -> dict[str, RegisterValue]:
        """ Update the register map with the latest values read from the inverter and return a combined dictionary of all data.

        Class is responsible for reading the data from the inverter and returning it as a dictionary.
        The class maintains the last successful reading and timestamp, and if a read fails,
        it will return the last known values if they are not too old, otherwise it will return an error message.

        Philosopy here is  to perform a series of modbus reads, setting a single error flag for the whole dataset
        on the failure of any read.
        read, check for a successful read of all data, and return the last complete data.
        If the read was not successful, then return the last known values if they are not too old, otherwise return an error message.
        """
        """
        Return the current data if valid, otherwise handle stale caching.

        Uses last successful data if it's not too old. Logs warnings or errors
        as needed.
        """
        if not self._runtime_data.modbus_client.register_map.is_error():
            # Success: cache data
            self._last_successful_data = current_data.copy()
            self._last_successful_timestamp = datetime.now()
            # Increment update counter
            self._update_cnt += 1
            if self._update_cnt >= 65535:
                self._update_cnt = 0
            current_data["update_cnt"] = self._update_cnt
            return current_data

        # Error: fallback to last known data
        if (
            self._last_successful_data
            and self._last_successful_timestamp
            and (datetime.now() - self._last_successful_timestamp).total_seconds() < self.max_stale_data_age
        ):
            _LOGGER.warning(
                "Using last known values (%.1f seconds old) due to communication error",
                (datetime.now() - self._last_successful_timestamp).total_seconds(),
            )
            return self._last_successful_data

        # No valid data to return
        _LOGGER.error(
            "No recent valid data available (last successful read: %s)",
            self._last_successful_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self._last_successful_timestamp else "never",
        )
        return {"faultmsg": "Communication lost with inverter"}
