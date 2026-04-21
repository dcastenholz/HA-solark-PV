import logging
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Callable, TypeVar

_LOGGER = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

def metric(func: F) -> F:
    func._is_metric = True  # mark method
    return func

class ReturnedDataType(StrEnum):
    REALTIME_DATA = "Real-time data"
    RECENT_DATA = "Recent cached data"
    NO_RECENT_DATA = "No recent cached data"
    NO_DATA = "No cached data"


class CoordinatorMetrics:
    def __init__(self) -> None:
        self._data_updating_count: int = 0
        self._data_updated_count: int = 0
        self._data_update_failed_count: int = 0

        self._last_startup_timestamp: datetime | None = None
        self._last_shutdown_timestamp: datetime | None = None

        self._last_data_reading_timestamp: datetime | None = None
        self._last_data_read_timestamp: datetime | None = None
        self._last_data_read_failed_timestamp =  None

        self._last_data_updating_timestamp: datetime | None = None
        self._last_data_updated_timestamp: datetime | None = None
        self._last_data_update_failed_timestamp: datetime | None = None

        self._last_data_read_result: bool = False
        self._last_data_update_result: bool = False

        self._last_return_stale_data: datetime | None = None
        self._last_return_no_data_timestamp: datetime | None = None
        self._last_returned_data_type: ReturnedDataType = ReturnedDataType.NO_DATA

        self._max_data_updated_duration: timedelta = timedelta(0)
        self._min_data_updated_duration: timedelta = timedelta.max

    # ----------------------------------
    # Update data lifecycle events
    # ----------------------------------
    def on_startup(self):
        '''Record the initialization of the coordinator and do any initialization'''
        self._last_startup_timestamp = datetime.now()
        return

    def on_data_updating(self):
        '''Record the start of the data update cycle and do any initialization'''
        self._data_updating_count += 1
        self._last_data_updating_timestamp = datetime.now()
        return

    def on_data_reading(self):
        '''Record the start of a modbus data read'''
        self._last_data_reading_timestamp = datetime.now()
        return

    def on_data_read_result(self, data_read_successful: bool):
        if data_read_successful:
            # Record the successful data read
            self._on_data_read()
            _LOGGER.debug("Last data read succeeded. Duration: %s", self.last_data_read_attempt_duration())
        else:
            # Record the unsuccessful data read
            self._on_data_read_failed()
            _LOGGER.error("Last data read failed. Duration: %s", self.last_data_read_attempt_duration())

    def on_data_update_result(self, data_update_successful: bool):
        if data_update_successful:
            # Record the successful data update
            self._on_data_updated()
        else:
            # Record the unsuccessful data update
            self._on_data_update_failed()

    def on_return_realtime_data(self):
        '''Record the return of stale data'''
        self._last_returned_data_type = ReturnedDataType.REALTIME_DATA
        return

    def on_return_recent_cached_data(self):
        '''Record the return of stale data'''
        self._last_return_stale_data = datetime.now()
        self._last_returned_data_type = ReturnedDataType.RECENT_DATA
        return

    def on_return_no_recent_cached_data(self):
        '''Record the return of stale data'''
        self._last_return_stale_data = datetime.now()
        self._last_returned_data_type = ReturnedDataType.RECENT_DATA
        return

    def on_return_no_cached_data(self):
        '''Record the return of no data'''
        self._last_return_no_data_timestamp = datetime.now()
        self._last_returned_data_type = ReturnedDataType.NO_DATA
        return

    def on_shutdown(self):
        '''Record the shutdown of the coordinator'''
        self._last_shutdown_timestamp = datetime.now()
        return

    # ----------------------------------
    # Properties for sensors
    # ----------------------------------
    @metric
    def data_updating_count(self) -> int:
        '''The number of update attempts since the coordinator was started.
        Enabling a disabled sensor in the UI will cause the coordinator to reload,
        causing a reset of this counter.'''
        return self._data_updating_count

    @metric
    def data_updated_count(self) -> int:
        '''The number of successful update results since the coordinator was started.
        Enabling a disabled sensor in the UI will cause the coordinator to reload,
        causing a reset of this counter.'''
        return self._data_updated_count

    @metric
    def data_update_failed_count(self) -> int:
        '''The number of unsuccessful update results since the coordinator was started.
        Enabling a disabled sensor in the UI will cause the coordinator to reload,
        causing a reset of this counter.'''
        return self._data_update_failed_count

    @metric
    def update_cnt(self) -> int:
        '''For backwards compatibility.
        The number of successful data updates since the coordinator was started.
        New underlying count property will not roll over under normal conditions.
        This will prevent the appearance of a restart, when in fact, the counter has just rolled over.'''
        return self._data_updated_count & 0xFFFF

    @metric
    def last_data_read_result(self) -> bool:
        return self._last_data_read_result

    @metric
    def last_data_update_result(self) -> bool:
        return self._last_data_update_result

    @metric
    def last_data_read_timestamp(self) -> datetime | None:
        return self._last_data_read_timestamp

    @metric
    def last_data_read_failed_timestamp(self) -> datetime | None:
        return self._last_data_read_failed_timestamp

    @metric
    def last_data_updated_timestamp(self) -> datetime | None:
        return self._last_data_updated_timestamp

    @metric
    def last_data_update_failed_timestamp(self) -> datetime | None:
        return self._last_data_update_failed_timestamp

    @metric
    def last_data_read_attempt_duration(self) -> timedelta | None:
        return self.update_duration(self._last_data_reading_timestamp, self.last_data_read_attempt_end_timestamp())

    @metric
    def last_data_update_attempt_duration(self) -> timedelta | None:
        return self.update_duration(self._last_data_updating_timestamp, self.last_data_update_attempt_end_timestamp())

    @metric
    def last_data_updated_duration(self) -> timedelta | None:
        return self.update_duration(self._last_data_updating_timestamp, self._last_data_updated_timestamp)

    @metric
    def last_returned_data_type(self) -> str | None:
        return self._last_returned_data_type.value

    @metric
    def max_data_updated_duration(self) -> timedelta | None:
        return self._max_data_updated_duration

    @metric
    def min_data_updated_duration(self) -> timedelta | None:
        return self._min_data_updated_duration

    # ----------------------------------
    # Storage and retrieval methods
    # ----------------------------------
    def to_dict(self) -> dict:
        return {
            "data_updating_count": self._data_updating_count,
            "data_updated_count": self._data_updated_count,
            "data_update_failed_count": self._data_update_failed_count,

            "last_startup_timestamp": self._last_startup_timestamp.isoformat() if self._last_startup_timestamp else None,
            "last_shutdown_timestamp": self._last_shutdown_timestamp.isoformat() if self._last_shutdown_timestamp else None,

            "last_data_reading_timestamp": self._last_data_reading_timestamp.isoformat() if self._last_data_reading_timestamp else None,
            "last_data_read_timestamp": self._last_data_read_timestamp.isoformat() if self._last_data_read_timestamp else None,
            "last_data_read_failed_timestamp": self._last_data_read_failed_timestamp.isoformat() if self._last_data_read_failed_timestamp else None,

            "last_data_updating_timestamp": self._last_data_updating_timestamp.isoformat() if self._last_data_updating_timestamp else None,
            "last_data_updated_timestamp": self._last_data_updated_timestamp.isoformat() if self._last_data_updated_timestamp else None,
            "last_data_update_failed_timestamp": self._last_data_update_failed_timestamp.isoformat() if self._last_data_update_failed_timestamp else None,

            "last_data_read_result": self._last_data_read_result,
            "last_data_update_result": self._last_data_update_result,

            "last_return_stale_data": self._last_return_stale_data.isoformat() if self._last_return_stale_data else None,
            "last_return_no_data_timestamp": self._last_return_no_data_timestamp.isoformat() if self._last_return_no_data_timestamp else None,

            "last_returned_data_type": self._last_returned_data_type.value if self._last_returned_data_type else None,
        }

    def from_dict(self, data: dict) -> None:
        def dt(v):
            return datetime.fromisoformat(v) if v else None

        self._data_updating_count = data.get("data_updating_count", 0)
        self._data_updated_count = data.get("data_updated_count", 0)
        self._data_update_failed_count = data.get("data_update_failed_count", 0)

        self._last_startup_timestamp = dt(data.get("last_startup_timestamp"))
        self._last_shutdown_timestamp = dt(data.get("last_shutdown_timestamp"))

        self._last_data_reading_timestamp = dt(data.get("last_data_reading_timestamp"))
        self._last_data_read_timestamp = dt(data.get("last_data_read_timestamp"))
        self._last_data_read_failed_timestamp = dt(data.get("last_data_read_failed_timestamp"))

        self._last_data_updating_timestamp = dt(data.get("last_data_updating_timestamp"))
        self._last_data_updated_timestamp = dt(data.get("last_data_updated_timestamp"))
        self._last_data_update_failed_timestamp = dt(data.get("last_data_update_failed_timestamp"))

        self._last_data_read_result = data.get("last_data_read_result", False)
        self._last_data_update_result = data.get("last_data_update_result", False)

        self._last_return_stale_data = dt(data.get("last_return_stale_data"))
        self._last_return_no_data_timestamp = dt(data.get("last_return_no_data_timestamp"))

        if data.get("last_returned_data_type"):
            self._last_returned_data_type = ReturnedDataType(data["last_returned_data_type"])

    # ----------------------------------
    # Private methods
    # ----------------------------------
    def last_data_read_attempt_end_timestamp(self) -> datetime | None:
        if self._last_data_read_result:
            return self._last_data_read_timestamp
        return self._last_data_read_failed_timestamp

    def last_data_update_attempt_end_timestamp(self) -> datetime | None:
        if self._last_data_update_result:
            return self._last_data_updated_timestamp
        return self._last_data_update_failed_timestamp

    def _on_data_read(self):
        '''Record the end of the successful modbus data read'''
        self._last_data_read_timestamp = datetime.now()
        self._last_data_read_result = True
        return

    def _on_data_read_failed(self):
        '''Record the end of the unsuccessful modbus data read'''
        self._last_data_read_failed_timestamp = datetime.now()
        self._last_data_read_result = False
        return

    def _on_data_updated(self):
        '''Record the end of the successful data update cycle'''
        # Increment update counter
        self._data_updated_count += 1
        self._last_data_updated_timestamp = datetime.now()
        self._last_data_update_result = True

        data_updated_timedelta = self.last_data_updated_duration()

        if data_updated_timedelta:
            if self._max_data_updated_duration < data_updated_timedelta:
                self._max_data_updated_duration = data_updated_timedelta
            if self._min_data_updated_duration > data_updated_timedelta:
                self._min_data_updated_duration = data_updated_timedelta

    def _on_data_update_failed(self):
        '''Record the end of the unsuccessful data update cycle'''
        # Increment update counter
        self._data_update_failed_count += 1
        self._last_data_update_failed_timestamp = datetime.now()
        self._last_data_update_result = False
        return

    @staticmethod
    def update_duration(start: datetime | None, end: datetime | None) -> timedelta | None:
        if start is None or end is None:
            return None
        return end - start
