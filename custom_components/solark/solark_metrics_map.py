from homeassistant.components.sensor import EntityCategory, SensorStateClass

from .coordinator_metrics import CoordinatorMetrics
from .metrics_map_entry import MetricsMapEntry
from .sensor_map import SensorMap


class SolArkMetricsMap(SensorMap):
    '''Class that declares performance metric sensors'''
    # ----------------------------------
    # Post processed sensor definitions
    # ----------------------------------
    # COUNT = MetricsMapEntry(key="modbus_read_duration", name="Modbus read duration", metric=CoordinatorMetrics.last_data_read_duration)
    METRICS_READ_DURATION = MetricsMapEntry(key="modbus_read_duration", name="Modbus read duration", metric=CoordinatorMetrics.last_data_read_duration)

    UPDATE_COUNTER = MetricsMapEntry(
        key="update_count", name="Update Count", icon="mdi:information-outline", metric=CoordinatorMetrics.update_count)

    # '''For backwards compatibility.
    # New underlying count property will not roll over under normal conditions.
    # This will prevent the appearance of a restart, when in fact, the counter has just rolled over.'''
    # UPDATE_CNT = MetricsMapEntry(
    #     key="update_cnt", name="Update Count - 16 bit rollover", icon="mdi:information-outline", entity_category = EntityCategory.DIAGNOSTIC)

    # UPDATE_COUNTER = SensorMapEntry(
    #     key="update_count", name="Update Count", icon="mdi:information-outline", state_class=SensorStateClass.TOTAL,
    #     on_data_updated=update_count_data_updated)

    # '''For backwards compatibility.
    # New underlying count property will not roll over under normal conditions.
    # This will prevent the appearance of a restart, when in fact, the counter has just rolled over.'''
    # UPDATE_CNT = SensorMapEntry(
    #     key="update_cnt", name="Update Count - 16 bit rollover", icon="mdi:information-outline", state_class=SensorStateClass.TOTAL,
    #     entity_category = EntityCategory.DIAGNOSTIC, on_data_updated=update_cnt_data_updated)