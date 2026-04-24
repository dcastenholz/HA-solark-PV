from homeassistant.config_entries import ConfigEntry

from .base_map import BaseMap
from .base_map_entry import BaseEntry
from .entity_description import EntityDescriptionHelper
from .solark_metrics_map import SolArkMetricsMap
from .solark_register_map import SolArkRegisterMap
from .solark_sensor_map import SolArkSensorMap


class BaseEntryList(list[BaseEntry]):
    ENABLED_BY_DEFAULT_CLASSIC: list[BaseEntry] = [
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
        SolArkMetricsMap.UPDATE_SUCCESSFUL_COUNT,
    ]


    @staticmethod
    def _set_enabled_by_default(base_map_entry_list: list[BaseEntry]) -> None:
        EntityDescriptionHelper.set_map_entity_registry_enabled_default(base_map_entry_list, True)

    @classmethod
    def set_config_enabled_by_default(cls, entry: ConfigEntry) -> None:
        # TODO - Get the list from the config entry
        cls._set_enabled_by_default(BaseEntryList.ENABLED_BY_DEFAULT_CLASSIC)

    @classmethod
    def set_map_enabled_by_default(cls, base_map: BaseMap) -> None:
        EntityDescriptionHelper.set_map_entity_registry_enabled_default(base_map, True)
