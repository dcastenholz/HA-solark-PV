from datetime import datetime, timedelta


class CoordinatorMetrics:
    _update_count: int = 0
    _last_start_timestamp: datetime
    _last_complete_timestamp: datetime
    _last_successful_timestamp: datetime
    _last_unsuccessful_timestamp: datetime

    def on_startup(self):
        self._update_count = 0
        return

    def on_start(self):
        self._last_start_timestamp = datetime.now()
        return

    def on_success(self):
        self._last_complete_timestamp = datetime.now()
        # Increment update counter
        self._update_count += 1
        self._last_successful_timestamp = datetime.now()
        return

    def on_failure(self):
        self._last_complete_timestamp = datetime.now()
        self._last_unsuccessful_timestamp = datetime.now()
        return

    @property
    def update_count(self) -> int:
        return self._update_count

    @property
    def last_successful_timestamp(self) -> datetime:
        return self._last_successful_timestamp

    @property
    def last_unsuccessful_timestamp(self) -> datetime:
        return self._last_unsuccessful_timestamp

    @property
    def last_update_duration(self) -> timedelta:
        return self._last_complete_timestamp - self._last_start_timestamp
