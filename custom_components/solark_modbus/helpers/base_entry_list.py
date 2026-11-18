"""Helpers for setting default enabled SolArk sensors."""

from homeassistant.config_entries import ConfigEntry

from ..entry_map.base_entry import BaseEntry
from ..entry_map.base_map import BaseMap
from ..helpers.entity_description_helper import EntityDescriptionHelper
from ..maps.solark_metrics_map import SolArkMetricsMap
from ..maps.solark_register_map import SolArkRegisterMap
from ..maps.solark_sensor_map import SolArkSensorMap


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

    ENABLED_BY_DEFAULT_TOU: list[BaseEntry] = [
        SolArkRegisterMap.TIMEOFUSE_ENABLED_RAW,
        SolArkRegisterMap.TIMEOFUSE_1_TIME,
        SolArkRegisterMap.TIMEOFUSE_2_TIME,
        SolArkRegisterMap.TIMEOFUSE_3_TIME,
        SolArkRegisterMap.TIMEOFUSE_4_TIME,
        SolArkRegisterMap.TIMEOFUSE_5_TIME,
        SolArkRegisterMap.TIMEOFUSE_6_TIME,
        SolArkRegisterMap.TIMEOFUSE_1_POWER,
        SolArkRegisterMap.TIMEOFUSE_2_POWER,
        SolArkRegisterMap.TIMEOFUSE_3_POWER,
        SolArkRegisterMap.TIMEOFUSE_4_POWER,
        SolArkRegisterMap.TIMEOFUSE_5_POWER,
        SolArkRegisterMap.TIMEOFUSE_6_POWER,
        SolArkRegisterMap.TIMEOFUSE_1_VOLTAGE,
        SolArkRegisterMap.TIMEOFUSE_2_VOLTAGE,
        SolArkRegisterMap.TIMEOFUSE_3_VOLTAGE,
        SolArkRegisterMap.TIMEOFUSE_4_VOLTAGE,
        SolArkRegisterMap.TIMEOFUSE_5_VOLTAGE,
        SolArkRegisterMap.TIMEOFUSE_6_VOLTAGE,
        SolArkRegisterMap.TIMEOFUSE_1_SOC,
        SolArkRegisterMap.TIMEOFUSE_2_SOC,
        SolArkRegisterMap.TIMEOFUSE_3_SOC,
        SolArkRegisterMap.TIMEOFUSE_4_SOC,
        SolArkRegisterMap.TIMEOFUSE_5_SOC,
        SolArkRegisterMap.TIMEOFUSE_6_SOC,
        SolArkRegisterMap.TIMEOFUSE_1_CHARGE_SELL,
        SolArkRegisterMap.TIMEOFUSE_2_CHARGE_SELL,
        SolArkRegisterMap.TIMEOFUSE_3_CHARGE_SELL,
        SolArkRegisterMap.TIMEOFUSE_4_CHARGE_SELL,
        SolArkRegisterMap.TIMEOFUSE_5_CHARGE_SELL,
        SolArkRegisterMap.TIMEOFUSE_6_CHARGE_SELL,
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
        cls._set_enabled_by_default(BaseEntryList.ENABLED_BY_DEFAULT_TOU)

    @classmethod
    def set_map_enabled_by_default(cls, base_map: BaseMap) -> None:
        """Set all entries in a map as enabled by default."""
        EntityDescriptionHelper.set_map_entity_registry_enabled_default(base_map, True)
