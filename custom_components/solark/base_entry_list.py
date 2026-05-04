"""Helpers for setting default enabled SolArk sensors."""

from homeassistant.config_entries import ConfigEntry

from .base_entry import BaseEntry
from .base_map import BaseMap
from .entity_description_helper import EntityDescriptionHelper
from .solark_metrics_map import SolArkMetricsMap
from .solark_register_map import SolArkRegisterMap
from .solark_sensor_map import SolArkSensorMap


class BaseEntryList(list[BaseEntry]):
    """Collections of predefined map entries."""

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
        """Enable the sensors based on configuration choices by user."""
        # TODO - Get the list from the config entry
        # For now, just enable the sensors that were enabled by the previous version of the integration.
        cls._set_enabled_by_default(BaseEntryList.ENABLED_BY_DEFAULT_CLASSIC)

    @classmethod
    def set_map_enabled_by_default(cls, base_map: BaseMap) -> None:
        """Set all entries in a map as enabled by default."""
        EntityDescriptionHelper.set_map_entity_registry_enabled_default(base_map, True)
