import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_MAX_STALE_DATA_AGE_SECONDS
from .coordinator_data import CoordinatorData
from .data import SolArkData
from .modbus_client import SolArkModbusClient
from .register_value_types import SensorValue
from .solark_register_map import SolArkRegisterMap
from .solark_sensor_map import SolArkSensorMap

_LOGGER = logging.getLogger(__name__)

class SolArkCoordinator(DataUpdateCoordinator[dict]):
    """ Update the register map with the latest values read from the inverter and return a combined
    dictionary of all data.

    Class is responsible for reading the data from the inverter and returning it as a dictionary.
    The class maintains the last successful reading and timestamp, and if a read fails,
    it will return the last known values if they are not too old, otherwise it will return an error message.

    Philosopy here is  to perform a series of modbus reads, setting a single error flag for the whole dataset
    on the failure of any read.
    read, check for a successful read of all data, and return the last complete data.
    If the read was not successful, then return the last known values if they are not too old,
    otherwise return an error message.
    """

    _runtime_data: SolArkData
    _data_read_error: bool = False

    def __init__(self, runtime_data: SolArkData):
        # Register the coordinator with the runtime_data
        self._runtime_data = runtime_data
        self._runtime_data.coordinator = self

        self._runtime_data.on_startup()

        self._last_successful_data: dict[str, SensorValue] | None = None
        self._last_successful_timestamp: datetime | None = None
        self.max_stale_data_age_seconds = DEFAULT_MAX_STALE_DATA_AGE_SECONDS  # seconds

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

    async def _async_update_data(self) -> dict[str, Any]:
        """Read the data from the inverter and return it as a dictionary."""
        register_map: SolArkRegisterMap = self._runtime_data.register_map
        calculated_sensor_map: SolArkSensorMap = self._runtime_data.calculated_sensor_map

        # TODO - Move to runtime_data??
        register_map.set_error(False)  # Initialize the register map before reading

        data_read_successful = await self._async_data_read()

        if data_read_successful:
            # If we already have a read failure, post processing is unnecessary and may fail as well.
            try:
                await self.hass.async_add_executor_job(register_map.on_data_updated)
                await self.hass.async_add_executor_job(calculated_sensor_map.on_data_updated)

            except Exception as e:
                data_read_successful = False
                _LOGGER.exception("Unexpected error post processing inverter data: %s", e)

            _LOGGER.debug("Last data read duration: %s", self._runtime_data.coordinator_metrics.last_update_duration)

        # Return the current data if valid, otherwise return cached previously read data.
        if data_read_successful:
            return self._runtime_data.current_data
        else:
            return self._get_fallback_data()

    async def _async_data_read(self) -> bool:
        # ----------------------------------
        # Data update started
        # ----------------------------------
        self._runtime_data.on_data_reading()

        modbus_client: SolArkModbusClient = self._runtime_data.modbus_client

        if not self.has_inverter_data:  # Inverter serial number is only fetched once
            try:
                # TODO - revisit the success and has_inverter_data logic.
                success = await self.hass.async_add_executor_job(modbus_client.read_modbus_inverter_data)
                self.has_inverter_data = True

            except Exception as e:
                success = False
                _LOGGER.exception("Unexpected error reading inverter data: %s", e)

        success: bool = False
        try:
            # Read realtime data
            success = await self.hass.async_add_executor_job(modbus_client.read_modbus_realtime_data)

        except Exception as e:
            _LOGGER.exception("Unexpected error reading realtime data: %s", e)

        if success:
            self._runtime_data.on_data_read()
        else:
            # Just record the failure.
            self._runtime_data.on_data_read_failed()

        # ----------------------------------
        # Data update completed
        # ----------------------------------
        return success

    def _get_fallback_data(self) -> dict[str, SensorValue]:
        """Use last successful data if it's not too old.
         Logs warnings or errors as needed."""

        # Error: fallback to last known data
        if  self._runtime_data.last_successful_read_data:
            data: CoordinatorData = self._runtime_data.last_successful_read_data

            if data.age.seconds < self.max_stale_data_age_seconds:
                _LOGGER.warning(
                "Using last known values (%.1f seconds old) due to communication error",
                data.age.seconds,
            )
            return self._runtime_data.last_successful_read_data.data

        # No valid data to return
        _LOGGER.error(
            "No recent valid data available (last successful read: %s)",
            self._last_successful_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self._last_successful_timestamp else "never",
        )
        return {"faultmsg": "Communication lost with inverter"}

    async def async_stop(self, *_):
        """Stop coordinator updates and close the client."""
        try:
            await self.hass.async_add_executor_job(self._runtime_data.modbus_client.close)
        except Exception as exc:
            _LOGGER.error("Error stopping coordinator: %s", exc, exc_info=True)
