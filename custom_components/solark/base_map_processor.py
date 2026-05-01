import logging

from .data import SolArkData
from .register_map import RegisterMap
from .sensor_map import SensorMap

_LOGGER = logging.getLogger(__name__)

class BaseMapProcessor():
    register_maps: list[RegisterMap]

    sensor_maps: list[SensorMap]

    metrics_maps: list[SensorMap]

    def __init__(self, runtime_data: SolArkData):
        self.register_maps = [runtime_data.register_map]
        self.sensor_maps = [runtime_data.calculated_sensor_map]
        self.metrics_maps = [runtime_data.metrics_map]

    def post_process(self) -> bool:
        pipeline_ok = True
        try:
            for map in self.register_maps:
                # Post-process the register map entries after reading the raw values from the inverter.
                # TODO - Handle case where the dependency registers were not read. Value is None
                for entry in map:
                    entry.process_sensor_value(map.runtime_data)
        except Exception as e:
            pipeline_ok = False
            _LOGGER.exception("Unexpected error setting register values: %s", e)


        if pipeline_ok:
            try:
                for map in self.sensor_maps:
                    for entry in map:
                        entry.process_sensor_value(map.runtime_data)
            except Exception as e:
                pipeline_ok = False
                _LOGGER.exception("Unexpected error post processing sensor map data: %s", e)

        return pipeline_ok

    def post_process_metrics_maps(self) -> bool:
        pipeline_ok = True
        try:
            for map in self.metrics_maps:
                for entry in map:
                    entry.process_sensor_value(map.runtime_data)
        except Exception as e:
            pipeline_ok = False
            _LOGGER.exception("Unexpected error post processing metrics map data: %s", e)
        return pipeline_ok
