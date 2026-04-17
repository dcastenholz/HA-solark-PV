from datetime import datetime, timedelta


class CoordinatorMetrics:
    _update_count: int = 0

    _last_startup_timestamp: datetime
    _last_shutdown_timestamp: datetime
    _last_updating_timestamp: datetime
    _last_updated_timestamp: datetime
    _last_update_failed_timestamp: datetime

    def on_startup(self):
        self._update_count = 0
        return

    def on_shutdown(self):
        self._last_shutdown_timestamp = datetime.now()
        return

    def on_updating(self):
        self._last_startup_timestamp = datetime.now()
        return

    def on_updated(self):
        self._last_updating_timestamp = datetime.now()
        # Increment update counter
        self._update_count += 1
        self._last_updated_timestamp = datetime.now()
        return

    def on_update_failed(self):
        self._last_updating_timestamp = datetime.now()
        self._last_update_failed_timestamp = datetime.now()
        return

    @property
    def update_count(self) -> int:
        return self._update_count

    @property
    def last_successful_timestamp(self) -> datetime:
        return self._last_updated_timestamp

    @property
    def last_failure_timestamp(self) -> datetime:
        return self._last_update_failed_timestamp

    @property
    def last_update_duration(self) -> timedelta:
        return self._last_updating_timestamp - self._last_startup_timestamp
