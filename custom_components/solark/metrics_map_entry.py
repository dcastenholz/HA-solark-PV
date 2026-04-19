from typing import Any, Callable, Unpack

from .base_map_entry import BaseMapEntry
from .coordinator_metrics import CoordinatorMetrics
from .sensor_entity_description import SensorClass, SolArkSensorEntityDescription
from .sensor_map_entry import SensorMapEntryOptional


class MetricsMapEntry(BaseMapEntry["MetricsMapEntry", "SolArkSensorEntityDescription"]):
    DEFAULTS = {
        "sensor_class": SensorClass.METRICS,
    }

    def __init__(
        self,
        key: str,
        name: str,
        metric: Callable[[CoordinatorMetrics], Any],
        **kwargs: Unpack[SensorMapEntryOptional],
    ) -> None:
        super().__init__(key, name, **kwargs)

        self._entity_description = SolArkSensorEntityDescription.from_kwargs(
            key=key,
            name=name,
            opts=self.opts,
        )

        self._metric = metric

        # # -----------------------------
        # # validate metric
        # # -----------------------------
        # if not isinstance(metric, property):
        #     raise TypeError(f"metric must be a property, got {type(metric)!r}")

        # if metric.fget is None or not getattr(metric.fget, "_is_metric", False):
        #     raise TypeError(
        #         "metric must be a @metric_property (decorated property)"
        #     )

        # self._metric = metric

    def get_value(self, runtime_data) -> Any:
        return self._metric(runtime_data.coordinator_metrics)