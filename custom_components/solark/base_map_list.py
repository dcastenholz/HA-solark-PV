from dataclasses import replace

from .base_map_entry import BaseMapEntry
from .config_entry import SolArkConfigEntry
from .solark_metrics_map import SolArkMetricsMap
from .solark_register_map import SolArkRegisterMap
from .solark_sensor_map import SolArkSensorMap


class BaseMapEntryList(list[BaseMapEntry]):
    ENABLED_BY_DEFAULT_CLASSIC: list[BaseMapEntry] = [
        SolArkRegisterMap.DAILYINV_E,
        SolArkRegisterMap.TOTALGRID_E,
        SolArkRegisterMap.DAILYBATT_C_E,
        SolArkRegisterMap.DAILYBATT_D_E,
        SolArkRegisterMap.DAILYGRIDBUY_E,
        SolArkRegisterMap.DAILYGRIDSELL_E,
        SolArkRegisterMap.GRIDFREQ,
        SolArkRegisterMap.DAILYLOAD_E,
        SolArkRegisterMap.TOTALLOAD_E,
        SolArkRegisterMap.TOTALINV_E,
        SolArkRegisterMap.DAILYPV_E,
        SolArkRegisterMap.INVL1L2_V,
        SolArkRegisterMap.GEN_P,
        SolArkRegisterMap.GRID_P,
        SolArkRegisterMap.INVL1_P,
        SolArkRegisterMap.INVL2_P,
        SolArkRegisterMap.INV_P,
        SolArkRegisterMap.LOAD_P,
        SolArkRegisterMap.BATT_V,
        SolArkRegisterMap.PV1_P,
        SolArkRegisterMap.PV2_P,
        SolArkRegisterMap.PV3_P,
        SolArkRegisterMap.BATT_P,
        SolArkRegisterMap.BATT_C,

        SolArkSensorMap.FAULTMSG,
        SolArkMetricsMap.UPDATE_COUNTER,
    ]

    # def set_enabled_by_default(entry_list: list[BaseMapEntry]):
    #     for entry in entry_list:
    #         entry.entity_description.entity_registry_enabled_default = True


    @classmethod
    def set_enabled_by_default(cls, entry_list: list[BaseMapEntry]) -> None:
        enabled_keys = {e.entity_description.key for e in BaseMapEntryList.ENABLED_BY_DEFAULT_CLASSIC}

        for entry in entry_list:
            if entry.entity_description.key in enabled_keys:
                entry.entity_description = replace(
                    entry.entity_description,
                    entity_registry_enabled_default=True,
                )

    @classmethod
    def set_config_enabled_by_default(cls, entry: SolArkConfigEntry) -> None:
        # TODO - Get the list from the config entry
        cls.set_enabled_by_default(BaseMapEntryList.ENABLED_BY_DEFAULT_CLASSIC)