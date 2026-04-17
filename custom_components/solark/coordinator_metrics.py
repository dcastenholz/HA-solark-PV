from datetime import datetime, timedelta


class CoordinatorMetrics:
    _update_count: int = 0

    _last_startup_timestamp: datetime
    _last_shutdown_timestamp: datetime

    _last_data_reading_timestamp: datetime
    _last_data_read_timestamp: datetime
    _last_data_read_failed_timestamp: datetime
    _last_data_updated_timestamp: datetime
    _last_updated_timestamp: datetime

    # ----------------------------------
    # Update data lifecycle events
    # ----------------------------------
    def on_startup(self):
        self._last_startup_timestamp = datetime.now()
        self._update_count = 0
        return

    def on_data_reading(self):
        self._last_data_reading_timestamp = datetime.now()
        return

    def on_data_read(self):
        self._last_data_read_timestamp = datetime.now()
        return

    def on_data_read_failed(self):
        self._last_data_read_failed_timestamp = datetime.now()
        return

    def on_data_updated(self):
        # Increment update counter
        self._update_count += 1
        self._last_data_updated_timestamp = datetime.now()
        return

    def on_shutdown(self):
        self._last_shutdown_timestamp = datetime.now()
        return

    @property
    def update_count(self) -> int:
        return self._update_count

    @property
    def last_updated_timestamp(self) -> datetime:
        return self._last_updated_timestamp

    @property
    def last_data_read_failed_timestamp(self) -> datetime:
        return self._last_data_read_failed_timestamp

    @property
    def last_data_read_duration(self) -> timedelta:
        return self._last_data_read_timestamp - self._last_data_reading_timestamp
