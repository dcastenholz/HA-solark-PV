import logging
from datetime import timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .coordinator_data import CoordinatorData
from .coordinator_metrics import CoordinatorMetrics
from .data import SolArkData
from .data_change_dispatcher import DataChangeDispatcher
from .data_change_handlers import DatChangeHandlers
from .modbus_client import SolArkModbusClient
from .register_value_types import SensorValue

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
    _coordinator_metrics: CoordinatorMetrics

    def __init__(self, runtime_data: SolArkData):
        # Register the coordinator with the runtime_data
        self._runtime_data = runtime_data
        self._runtime_data.coordinator = self

        # Set up data change listener to do special handling when registered data entries change.
        self._dispatcher = DataChangeDispatcher()
        self._data_change_handlers = DatChangeHandlers(self._runtime_data)
        # Set the serial number in the device after it is read or changes.
        self._dispatcher.register(self._runtime_data.register_map.SN, self._data_change_handlers.SN_change_handler)

        self.coordinator_metrics = CoordinatorMetrics()
        self.coordinator_metrics.on_startup()

        super().__init__(
            runtime_data.hass,
            _LOGGER,
            name=self._runtime_data.name,
            update_interval=timedelta(seconds=runtime_data.scan_interval),
        )

        # We want to attempt read the inverter information registers until we have read them successfully a single time.
        self.has_inverter_data = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Read the data from the inverter and return it as a dictionary."""

        self.coordinator_metrics.on_data_updating()
        return_data: dict[str, Any]

        # Perform the required modbus data reads
        data_read_successful: bool = await self._async_data_read()

        if data_read_successful:
            # If we already have a read failure, post processing is unnecessary and may fail as well.
            try:
                await self.hass.async_add_executor_job(self._runtime_data.register_map.on_data_updated)
                await self.hass.async_add_executor_job(self._runtime_data.calculated_sensor_map.on_data_updated)

            except Exception as e:
                data_read_successful = False
                _LOGGER.exception("Unexpected error post processing inverter data: %s", e)

            _LOGGER.debug("Last data read duration: %s", self.coordinator_metrics.last_data_read_duration)

        # Return the current data if valid, otherwise return cached previously read data.
        if data_read_successful:
            self._runtime_data.on_data_updated()
            self.coordinator_metrics.on_data_updated()

            self._dispatcher.dispatch(self._runtime_data)

            return_data = self._runtime_data.current_data
        else:
            return_data = self._get_fallback_data()

        return return_data | self._runtime_data.metrics_map.data

    async def _async_data_read(self) -> bool:
        modbus_client: SolArkModbusClient = self._runtime_data.modbus_client

        # Initialize the register map prior to attempting read
        self._runtime_data.register_map.init()

        # ----------------------------------
        # Modbus data read starting
        # ----------------------------------
        self.coordinator_metrics.on_data_reading()

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
            # record the success of the data read
            self.coordinator_metrics.on_data_read()
        else:
            # Just record the failure of the data read
            self.coordinator_metrics.on_data_read_failed()

        # ----------------------------------
        # Modbus data read completed
        # ----------------------------------
        return success

    def _get_fallback_data(self) -> dict[str, SensorValue]:
        """Use last successful data if it's not too old.
         Logs warnings or errors as needed."""

        # Error: fallback to last known data
        if self._runtime_data.last_data_updated:
            data: CoordinatorData = self._runtime_data.last_data_updated

            # Test cached data to see if the user config says it is too stale
            if data.age.seconds < self._runtime_data.config_data.max_stale_data_age_seconds:
                # Data is NOT too stale, so use it
                _LOGGER.warning(
                    "Using last known values (%.1f seconds old) due to communication error",
                    data.age.seconds,
                )
                # Record the return of stale data
                self.coordinator_metrics.on_return_stale_data()
                return self._runtime_data.last_data_updated.data

            # Data is too stale, so log error
            _LOGGER.error(
                "No recent valid data available (last successful read: %s)",
                data.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            )
        else:
            _LOGGER.error("No successful data read since integration was started")

        # TODO - implement separate sensor for this
        # Record the return of stale data
        self.coordinator_metrics.on_return_stale_data()
        return {"faultmsg": "Communication lost with inverter"}

    async def async_stop(self, *_):
        """Stop coordinator updates and close the client."""
        try:
            await self.hass.async_add_executor_job(self._runtime_data.modbus_client.close)
        except Exception as exc:
            _LOGGER.error("Error stopping coordinator: %s", exc, exc_info=True)

        self._dispatcher.clear()
        self.coordinator_metrics.on_shutdown()
