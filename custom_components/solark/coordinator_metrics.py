from datetime import datetime, timedelta
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

def metric(func: F) -> F:
    func._is_metric = True  # mark method
    return func


class CoordinatorMetrics:
    _update_count: int = 0

    _last_startup_timestamp: datetime | None
    _last_shutdown_timestamp: datetime | None

    _last_data_updating_timestamp: datetime | None
    _last_data_reading_timestamp: datetime | None
    _last_data_read_timestamp: datetime | None
    _last_data_read_failed_timestamp: datetime | None
    _last_data_updated_timestamp: datetime | None
    _last_return_stale_data: datetime | None
    _last_return_no_data_timestamp: datetime | None

    # ----------------------------------
    # Update data lifecycle events
    # ----------------------------------
    def on_startup(self):
        '''Record the initialization of the coordinator and do any initialization'''
        self._last_startup_timestamp = datetime.now()
        self._update_count = 0
        return

    def on_data_updating(self):
        '''Record the start of the data update cycle and do any initialization'''
        self._last_data_updating_timestamp = datetime.now()
        return

    def on_data_reading(self):
        '''Record the start of a modbus data read'''
        self._last_data_reading_timestamp = datetime.now()
        return

    def on_data_read(self):
        '''Record the end of a successful modbus data read'''
        self._last_data_read_timestamp = datetime.now()
        return

    def on_data_read_failed(self):
        '''Record the end of an unsuccessful modbus data read'''
        self._last_data_read_failed_timestamp = datetime.now()
        return

    def on_data_updated(self):
        '''Record the end of the data update cycle'''
        # Increment update counter
        self._update_count += 1
        self._last_data_updated_timestamp = datetime.now()
        return

    def on_data_update_failed(self):
        '''Record the end of the data update cycle'''
        # Increment update counter
        self._last_data_updated_timestamp = datetime.now()
        return

    def on_return_stale_data(self):
        '''Record the return of stale data'''
        self._last_return_stale_data = datetime.now()
        return

    def on_return_no_data(self):
        '''Record the return of no data'''
        self._last_return_no_data_timestamp = datetime.now()
        return

    def on_shutdown(self):
        '''Record the shutdown of the coordinator'''
        self._last_shutdown_timestamp = datetime.now()
        return

    # ----------------------------------
    # Properties for sensors
    # ----------------------------------
    @metric
    def update_count(self) -> int:
        return self._update_count

    @metric
    def last_updated_timestamp(self) -> datetime | None:
        return self._last_data_updated_timestamp

    # @metric
    def last_data_read_failed_timestamp(self) -> datetime | None:
        return self._last_data_read_failed_timestamp

    @metric
    def last_data_read_duration(self) -> timedelta | None:
        if self._last_data_read_timestamp is None or self._last_data_reading_timestamp is None:
            return None
        return self._last_data_read_timestamp - self._last_data_reading_timestamp

    # def data(self) -> dict[str, Any]:
    #     data_dict: dict[str, Any] = {}
    #     data_dict["update_count"] = self.update_count
    #     return data_dict

    @property
    def data(self) -> dict[str, Any]:
        result: dict[str, Any] = {}

        for name in dir(type(self)):
            attr = getattr(type(self), name, None)

            if callable(attr) and getattr(attr, "_is_metric", False):
                result[name] = getattr(self, name)()  # call method

        return result
