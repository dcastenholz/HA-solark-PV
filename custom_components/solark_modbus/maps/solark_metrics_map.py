"""Metrics sensor map for SolArk."""

from .._binary_sensor.binary_sensor_entry import MetricsSuccessEntry
from ..coordinator.coordinator_metrics import CoordinatorMetrics as CM
from ..entry_map.sensor_entry import MetricsEntry
from ..entry_map.sensor_map import SensorMap


class SolArkMetricsMap(SensorMap):
    '''Class that declares performance metric sensors'''

    UPDATE_ATTEMPT_COUNT = MetricsEntry(key="updating_count", name="Attempted Update Count", metric=CM.data_updating_count)
    UPDATE_SUCCESSFUL_COUNT = MetricsEntry(key="updated_count", name="Successful Update Count", metric=CM.data_updated_count)
    UPDATE_FAILED_COUNT = MetricsEntry(key="update_failed_count", name="Failed Update Count", metric=CM.data_update_failed_count)
    # For backwards compatibility.
    # New underlying count property will not roll over under normal conditions.
    # This will prevent the appearance of a restart, when in fact, the counter has just rolled over.
    UPDATE_CNT_DEPRECATED = MetricsEntry(key="update_cnt", name="Update Count - 16 bit rollover", metric=CM.update_cnt)

    READ_RESULT = MetricsSuccessEntry(key="metric_modbus_read_result", name="Modbus Data Read Result", metric=CM.last_data_read_result)
    UPDATE_RESULT = MetricsSuccessEntry(key="metric_data_update_result", name="Data Update Result", metric=CM.last_data_update_result)

    READ_DURATION = MetricsEntry(key="metric_modbus_data_read_duration", name="Modbus Data Read Duration", metric=CM.last_data_read_attempt_duration)
    UPDATE_DURATION = MetricsEntry(key="metric_data_update_duration", name="Data Update Duration", metric=CM.last_data_update_attempt_duration)

    READ_SUCCESSFUL_TIMESTAMP = MetricsEntry(key="metric_modbus_data_read_timestamp", name="Last Successful Modbus Data Read", metric=CM.last_data_read_timestamp)
    UPDATE_SUCCESSFUL_TIMESTAMP = MetricsEntry(key="metric_data_updated_timestamp", name="Last Successful Data Update", metric=CM.last_data_updated_timestamp)

    READ_FAILED_TIMESTAMP = MetricsEntry(key="metric_modbus_data_read_failed_timestamp", name="Last Failed Modbus Data Read", metric=CM.last_data_read_failed_timestamp)
    UPDATE_FAILED_TIMESTAMP = MetricsEntry(key="metric_data_update_failed_timestamp", name="Last Failed Data Update", metric=CM.last_data_update_failed_timestamp)

    UPDATE_RETURN_TYPE = MetricsEntry(key="metric_data_update_return_type", name="Data Update Returned", metric=CM.last_returned_data_type)

    MAX_DATA_UPDATE_DURATION = MetricsEntry(key="metric_max_data_updated_duration", name="Max Data Update Duration", metric=CM.max_data_updated_duration)
    MIN_DATA_UPDATE_DURATION = MetricsEntry(key="metric_min_data_updated_duration", name="Min Data Update Duration", metric=CM.min_data_updated_duration)
