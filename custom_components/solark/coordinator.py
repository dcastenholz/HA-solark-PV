import logging
from datetime import timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .base_map_processor import BaseMapProcessor
from .coordinator_data import CoordinatorData
from .coordinator_metrics import CoordinatorMetrics
from .data import SolArkData
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

        self.coordinator_metrics = self._runtime_data.coordinator_metrics
        self.coordinator_metrics.on_startup()

        super().__init__(
            runtime_data.hass,
            _LOGGER,
            name=self._runtime_data.name,
            update_interval=timedelta(seconds=runtime_data.config_data.scan_interval),
        )

        _LOGGER.debug(
            "Scan interval set to %s seconds, Max stale data age set to %s seconds.",
            runtime_data.config_data.scan_interval,
            runtime_data.config_data.max_stale_data_age_seconds
        )

        # We want to attempt to read the inverter information registers until we have read them successfully a single time.
        self.has_inverter_data = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Read the data from the inverter and return it as a dictionary."""

        self.coordinator_metrics.on_data_updating()
        return_data: dict[str, Any]

        map_processor = BaseMapProcessor(self._runtime_data)

        # Perform the required modbus data reads
        pipeline_ok: bool = await self._async_read_registers()

        if pipeline_ok:
            pipeline_ok = await self.hass.async_add_executor_job(map_processor.post_process)

        self.coordinator_metrics.on_data_update_result(pipeline_ok)

        # Return the current data if valid, otherwise return cached previously read data.
        if pipeline_ok:
            # Save the new data for use if there is a future failure
            self._runtime_data.cache_updated_data()

            # Return the current data
            return_data = self._runtime_data.register_map.data | self._runtime_data.calculated_sensor_map.data
            self.coordinator_metrics.on_return_realtime_data()
        else:
            return_data = self._try_get_cached_data()

        # Set the sensor_values for all the metrics sensors
        await self.hass.async_add_executor_job(map_processor.post_process_metrics_maps)

        # Return a dictionary including the inverter data and the metrics data
        return return_data | self._runtime_data.metrics_map.data

    async def _async_read_registers(self) -> bool:
        modbus_client: SolArkModbusClient = self._runtime_data.modbus_client

        # Initialize the register map prior to attempting read
        self._runtime_data.register_map.init()

        # ----------------------------------
        # Modbus data read starting
        # ----------------------------------
        self.coordinator_metrics.on_data_reading()
        pipeline_ok: bool = True

        if not self.has_inverter_data:  # Inverter serial number is only fetched once
            try:
                # TODO - revisit the success and has_inverter_data logic.
                pipeline_ok = await self.hass.async_add_executor_job(modbus_client.read_modbus_inverter_data)
                self.has_inverter_data = True

            except Exception as e:
                pipeline_ok = False
                _LOGGER.exception("Unexpected error reading inverter data: %s", e)

        if pipeline_ok:
            try:
                # Read realtime data
                pipeline_ok = await self.hass.async_add_executor_job(modbus_client.read_modbus_realtime_data)

            except Exception as e:
                pipeline_ok = False
                _LOGGER.exception("Unexpected error reading realtime data: %s", e)

        self.coordinator_metrics.on_data_read_result(pipeline_ok)
        # ----------------------------------
        # Modbus data read completed
        # ----------------------------------
        return pipeline_ok

    def _try_get_cached_data(self) -> dict[str, SensorValue]:
        """Use last successful data if it's not too old.
         Logs warnings or errors as needed."""

        cached_data: CoordinatorData = self._runtime_data.last_data_updated

        # Error: attempt to fallback to recent cached data
        if cached_data is None:
            # There is no cached data yet, so return
            _LOGGER.error("Returning no data. No successful data update since integration was started.")
            # Record the return of no data
            self.coordinator_metrics.on_return_no_cached_data()
            return {"faultmsg": "Cannot communicate with inverter"}

        # We have cached data, now test to see if the user config says it is too stale
        if cached_data.age.seconds >= self._runtime_data.config_data.max_stale_data_age_seconds:
            # Data is too stale, so log error
            _LOGGER.warning(
                "Returning no data. No recent cached data available. Last successful update: %s.",
                cached_data.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            )
            # Record the return of no recent cached data
            self.coordinator_metrics.on_return_no_recent_cached_data()
            return {"faultmsg": "Lost communication with inverter"}

        # We have cached data, and it is recent, so use it!
        _LOGGER.warning(
            "Returning recent cached data (%.1f seconds old) due to communication error.",
            cached_data.age.seconds,
        )
        # Record the return of recent cached data
        self.coordinator_metrics.on_return_recent_cached_data()
        return cached_data.data

    async def async_stop(self, *_):
        """Stop coordinator updates and close the client."""
        try:
            await self.hass.async_add_executor_job(self._runtime_data.modbus_client.close)
        # TODO - log the full exception here to try to catch the reason for the spurious failures.
        except Exception as exc:
            _LOGGER.error("Error stopping coordinator: %s", exc, exc_info=True)

        # self._data_change_dispatcher.clear()
        self.coordinator_metrics.on_shutdown()
