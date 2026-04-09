from typing import TypeVar

from homeassistant.components.sensor import (
    EntityCategory,
    SensorStateClass,
)

from .register_map import RegisterMap
from .register_map_entry import (
    BatteryVoltageEntry,
    CurrentEntry,
    DataType,
    EnergyEntry,
    FrequencyEntry,
    GridVoltageEntry,
    PowerEntry,
    PVVoltageEntry,
    RawValueEntry,
    RegisterMapEntry,
    SOCEntry,
    StringEntry,
    SystemTimeEntry,
    TemperatureEntry,
    TimeOfUseEnabledEntry,
    TimeOfUseTimeEntry,
    UnitOfMeasure,
)

T = TypeVar("T", bound="RegisterMap")  # T is the real subclass

"""SolArk Modbus Register Map class"""
class SolArkRegisterMap(RegisterMap):
    SN = StringEntry(address=3, length=5, key="sn", name="Serial Number", icon="mdi:information-outline")
    INFO_FIRMWARE_S = RawValueEntry(address=11, key="info_firmware_s", name="Firmware S Raw", icon="mdi:information-outline")
    INFO_FIRMWARE_M = RawValueEntry(address=13, key="info_firmware_m", name="Firmware Control Board Raw", icon="mdi:information-outline")
    INFO_FIRMWARE_C = RawValueEntry(address=14, key="info_firmware_c", name="Firmware Communication Board Raw", icon="mdi:information-outline")
    INFO_RATED_POWER = PowerEntry(address=16, key="info_rated_power", scale=0.1, name="Rated Power", icon="mdi:solar-power", data_type=DataType.UINT32, entity_category=EntityCategory.DIAGNOSTIC)
    INFO_MPPT_PHASE_COUNTS_RAW = RawValueEntry(address=18, key="info_mppt_phase_raw", name="MPPT & Phase Info Raw Value")

    SYSTEM_TIME_YM_RAW = SystemTimeEntry(address=22, key="system_time_ym_raw", name="System Time Year Month Raw Value", exclude_from_recorder=True)
    SYSTEM_TIME_DH_RAW = SystemTimeEntry(address=23, key="system_time_DH_raw", name="System Time Day Hour Raw Value", exclude_from_recorder=True)
    SYSTEM_TIME_MS_RAW = SystemTimeEntry(address=24, key="system_time_ms_raw", name="System Time Minute Second Raw Value", exclude_from_recorder=True)

    DAILYINV_E = EnergyEntry(address=60, key="dailyinv_e", name="Daily Inverter Energy", data_type=DataType.INT16)
#    DAILYREA_E = EnergyEntry(address=61, key="dailyrea_e", name="Daily Reactive Energy", data_type=DataType.INT16)
    TOTALGRID_E = EnergyEntry(address=63, key="totalgrid_e", name="Total Grid Breaker Energy", data_type=DataType.INT32, entity_registry_enabled_default=True)
    DAILYBATT_C_E = EnergyEntry(address=70, key="daybattc_e", name="Daily Battery Charge Energy", data_type=DataType.UINT16, state_class=SensorStateClass.TOTAL_INCREASING, entity_registry_enabled_default=True)
    DAILYBATT_D_E = EnergyEntry(address=71, key="daybattd_e", name="Daily Battery Discharge Energy", data_type=DataType.UINT16, state_class=SensorStateClass.TOTAL_INCREASING, entity_registry_enabled_default=True)
    TOTALBATT_C_E = EnergyEntry(address=72, key="totalbattc_e", name="Total Battery Charge Energy", data_type=DataType.INT32)
    TOTALBATT_D_E = EnergyEntry(address=74, key="totalbattd_e", name="Total Battery Discharge Energy", data_type=DataType.INT32)
    DAILYGRIDBUY_E = EnergyEntry(address=76, key="dailygridbuy_e", name="Daily Grid Buy Energy", data_type=DataType.UINT16, state_class=SensorStateClass.TOTAL_INCREASING, entity_registry_enabled_default=True)
    DAILYGRIDSELL_E = EnergyEntry(address=77, key="dailygridsell_e", name="Daily Grid Sell Energy", data_type=DataType.UINT16, state_class=SensorStateClass.TOTAL_INCREASING, entity_registry_enabled_default=True)
    TOTALGRIDBUY_E_LOW_RAW = RawValueEntry(address=78, key="totalgridbuy_e_low", name="Total Grid Buy Energy - low word")
    GRIDFREQ = FrequencyEntry(address=79, key="gridfreq", name="Grid Frequency", entity_registry_enabled_default=True)
    TOTALGRIDBUY_E_HIGH_RAW = RawValueEntry(address=80, key="totalgridbuy_e_high", name="Total Grid Buy Energy - high word")
    TOTALGRIDSELL_E = EnergyEntry(address=81, key="totalsell_e", name="Total Grid Sell Energy", data_type=DataType.INT32)
    DAILYLOAD_E = EnergyEntry(address=84, key="dailyload_e", name="Daily Load Energy", data_type=DataType.UINT16, state_class=SensorStateClass.TOTAL_INCREASING)
    TOTALLOAD_E = EnergyEntry(address=85, key="totalload_e", name="Total Load Energy", data_type=DataType.INT32, entity_registry_enabled_default=True)
    DCHSTempC = TemperatureEntry(address=90, key="dchstempc", name="DC Heatsink Temperature")
    ACHSTempC = TemperatureEntry(address=91, key="achstempc", name="AC Heatsink Temperature")
    TOTALINV_E = EnergyEntry(address=96, key="totalinv_e", name="Total PV Energy", data_type=DataType.INT32, entity_registry_enabled_default=True)
    FAULT_INFO_RAW = RawValueEntry(address=103, key="fault_info_raw", name="Inverter Fault Information Raw Value", data_type=DataType.UINT64, icon="mdi:message-alert-outline")
    CORR_BATT_CAP = RegisterMapEntry(address=107, key="corr_batt_cap", name="Corrected Battery Capacity", data_type=DataType.UINT16, icon="mdi:battery", unit_of_measurement=UnitOfMeasure.AH, state_class=None)
    DAILYPV_E = EnergyEntry(address=108, key="dailypv_e", name="Daily PV Energy", data_type=DataType.UINT16, state_class=SensorStateClass.TOTAL_INCREASING, entity_registry_enabled_default=True)

    PV1_V = PVVoltageEntry(address=109, key="pv1_v", name="PV1 Voltage")
    PV1_C = CurrentEntry(address=110, key="pv1_c", name="PV1 Current")
    PV2_V = PVVoltageEntry(address=111, key="pv2_v", name="PV2 Voltage")
    PV2_C = CurrentEntry(address=112, key="pv2_c", name="PV2 Current")
    PV3_V = PVVoltageEntry(address=113, key="pv3_v", name="PV3 Voltage")
    PV3_C = CurrentEntry(address=114, key="pv3_c", name="PV3 Current")

    GRIDL1N_V = GridVoltageEntry(address=150, key="gridl1n_v", name="Grid L1-N Voltage")
    GRIDL2N_V = GridVoltageEntry(address=151, key="gridl2n_v", name="Grid L2-N Voltage")
    GRIDL1L2_V = GridVoltageEntry(address=152, key="gridl1l2_v", name="Grid L1-L2 Voltage")
    GRIDRELAY_V = GridVoltageEntry(address=153, key="gridrelay_v", name="Grid Relay Voltage")
    INVL1N_V = GridVoltageEntry(address=154, key="invl1n_v", name="Inverter L1-N Voltage")
    INVL2N_V = GridVoltageEntry(address=155, key="invl2n_v", name="Inverter L2-N Voltage")
    INVL1L2_V = GridVoltageEntry(address=156, key="invl1l2_v", name="Inverter L1-L2 Voltage", entity_registry_enabled_default=True)
    LOADL1_V = GridVoltageEntry(address=157, key="loadl1n_v", name="Load L1-N Voltage")
    LOADL2_V = GridVoltageEntry(address=158, key="loadl2n_v", name="Load L2-N Voltage")

    GRIDL1_C = CurrentEntry(address=160, key="gridl1_c", name="Grid L1 Current", icon="mdi:current-ac")
    GRIDL2_C = CurrentEntry(address=161, key="gridl2_c", name="Grid L2 Current", icon="mdi:current-ac")
    EXTLMTL1_C = CurrentEntry(address=162, key="extlmtl1_c", name="External Lmt L1 Current", icon="mdi:current-ac")
    EXTLMTL2_C = CurrentEntry(address=163, key="extlmtl2_c", name="External Lmt L2 Current", icon="mdi:current-ac")
    INVL1_C = CurrentEntry(address=164, key="invl1_c", name="Inverter L1 Current", icon="mdi:current-ac")
    INVL2_C = CurrentEntry(address=165, key="invl2_c", name="Inverter L2 Current", icon="mdi:current-ac")

    GEN_P = PowerEntry(address=166, key="gen_p", name="Gen Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    GRIDL1_P = PowerEntry(address=167, key="gridl1_p", name="Grid L1 Power", icon="mdi:solar-power")
    GRIDL2_P = PowerEntry(address=168, key="gridl2_p", name="Grid L2 Power", icon="mdi:solar-power")
    GRID_P = PowerEntry(address=169, key="grid_p", name="Total Grid Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    GRIDLMTL1_P = PowerEntry(address=170, key="gridlmtl1_p", name="Grid Limiter L1 Power", icon="mdi:solar-power")
    GRIDLMTL2_P = PowerEntry(address=171, key="gridlmtl2_p", name="Grid Limiter L2 Power", icon="mdi:solar-power")
    GRIDEXT_P = PowerEntry(address=172, key="gridext_p", name="Grid External Total Power", icon="mdi:solar-power")
    INVL1_P = PowerEntry(address=173, key="invl1_p", name="Inverter L1 Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    INVL2_P = PowerEntry(address=174, key="invl2_p", name="Inverter L2 Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    INV_P = PowerEntry(address=175, key="inv_p", name="Inverter Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    LOADL1_P = PowerEntry(address=176, key="loadl1_p", name="Load L1 Power", icon="mdi:solar-power")
    LOADL2_P = PowerEntry(address=177, key="loadl2_p", name="Load L2 Power", icon="mdi:solar-power")
    LOAD_P = PowerEntry(address=178, key="load_p", name="Load Power", icon="mdi:solar-power", entity_registry_enabled_default=True)

    LOADL1_C = CurrentEntry(address=179, key="loadl1_c", name="Load L1 Current", icon="mdi:current-ac")
    LOADL2_C = CurrentEntry(address=180, key="loadl2_c", name="Load L2 Current", icon="mdi:current-ac")

    GENL1L2_V = GridVoltageEntry(address=181, key="genl1l2_v", name="Generator L1-L2 Voltage")
    BATTTEMP_C = TemperatureEntry(address=182, key="batttempc", name="Battery Temperature")
    BATT_V = BatteryVoltageEntry(address=183, key="batt_v", name="Battery Voltage", entity_registry_enabled_default=True)
    BATT_SOC = SOCEntry(address=184, key="batt_soc", name="Battery State of Charge")

    PV1_P = PowerEntry(address=186, key="pv1_p", name="PV1 Input Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    PV2_P = PowerEntry(address=187, key="pv2_p", name="PV2 Input Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    PV3_P = PowerEntry(address=188, key="pv3_p", name="PV3 Input Power", icon="mdi:solar-power", entity_registry_enabled_default=True)

    BATT_P = PowerEntry(address=190, key="batt_p", name="Battery Power", icon="mdi:solar-power", entity_registry_enabled_default=True)
    BATT_C = CurrentEntry(address=191, key="batt_c", name="Battery Current", icon="mdi:current-dc", entity_registry_enabled_default=True)

    LOAD_FREQ = FrequencyEntry(address=192, key="loadfreq", name="Load Frequency")
    INVERTER_FREQ = FrequencyEntry(address=193, key="inverterfreq", name="Inverter Output Frequency")

    GRID_RLY_RAW = RawValueEntry(address=194, key="grid_rly_raw", name="Grid Relay Raw Value")
    GEN_RLY_RAW = RawValueEntry(address=195, key="gen_rly_raw", name="Generator Relay Raw Value")

    GEN_FREQ = FrequencyEntry(address=196, key="genfreq", name="Generator Relay Frequency")

    # ----------------------------
    # Time of use
    # ----------------------------
    TIMEOFUSE_ENABLED = RegisterMapEntry(address=248, key="timeofuse_enabled", data_type=DataType.UINT16, name="Time of Use Enabled")

    TIMEOFUSE_TIME_1 = TimeOfUseTimeEntry(address=250, key="timeofuse_time_1", name="Time of Use Time 1")
    TIMEOFUSE_TIME_2 = TimeOfUseTimeEntry(address=251, key="timeofuse_time_2", name="Time of Use Time 2")
    TIMEOFUSE_TIME_3 = TimeOfUseTimeEntry(address=252, key="timeofuse_time_3", name="Time of Use Time 3")
    TIMEOFUSE_TIME_4 = TimeOfUseTimeEntry(address=253, key="timeofuse_time_4", name="Time of Use Time 4")
    TIMEOFUSE_TIME_5 = TimeOfUseTimeEntry(address=254, key="timeofuse_time_5", name="Time of Use Time 5")
    TIMEOFUSE_TIME_6 = TimeOfUseTimeEntry(address=255, key="timeofuse_time_6", name="Time of Use Time 6")

    TIMEOFUSE_POWER_1 = PowerEntry(address=256, key="timeofuse_power_1", name="Time of Use Power 1")
    TIMEOFUSE_POWER_2 = PowerEntry(address=257, key="timeofuse_power_2", name="Time of Use Power 2")
    TIMEOFUSE_POWER_3 = PowerEntry(address=258, key="timeofuse_power_3", name="Time of Use Power 3")
    TIMEOFUSE_POWER_4 = PowerEntry(address=259, key="timeofuse_power_4", name="Time of Use Power 4")
    TIMEOFUSE_POWER_5 = PowerEntry(address=260, key="timeofuse_power_5", name="Time of Use Power 5")
    TIMEOFUSE_POWER_6 = PowerEntry(address=261, key="timeofuse_power_6", name="Time of Use Power 6")

    TIMEOFUSE_VOLTAGE_1 = BatteryVoltageEntry(address=262, key="timeofuse_voltage_1", name="Time of Use Voltage 1")
    TIMEOFUSE_VOLTAGE_2 = BatteryVoltageEntry(address=263, key="timeofuse_voltage_2", name="Time of Use Voltage 2")
    TIMEOFUSE_VOLTAGE_3 = BatteryVoltageEntry(address=264, key="timeofuse_voltage_3", name="Time of Use Voltage 3")
    TIMEOFUSE_VOLTAGE_4 = BatteryVoltageEntry(address=265, key="timeofuse_voltage_4", name="Time of Use Voltage 4")
    TIMEOFUSE_VOLTAGE_5 = BatteryVoltageEntry(address=266, key="timeofuse_voltage_5", name="Time of Use Voltage 5")
    TIMEOFUSE_VOLTAGE_6 = BatteryVoltageEntry(address=267, key="timeofuse_voltage_6", name="Time of Use Voltage 6")

    TIMEOFUSE_SOC_1 = SOCEntry(address=268, key="timeofuse_soc_1", name="Time of Use SOC 1")
    TIMEOFUSE_SOC_2 = SOCEntry(address=269, key="timeofuse_soc_2", name="Time of Use SOC 2")
    TIMEOFUSE_SOC_3 = SOCEntry(address=270, key="timeofuse_soc_3", name="Time of Use SOC 3")
    TIMEOFUSE_SOC_4 = SOCEntry(address=271, key="timeofuse_soc_4", name="Time of Use SOC 4")
    TIMEOFUSE_SOC_5 = SOCEntry(address=272, key="timeofuse_soc_5", name="Time of Use SOC 5")
    TIMEOFUSE_SOC_6 = SOCEntry(address=273, key="timeofuse_soc_6", name="Time of Use SOC 6")

    TIMEOFUSE_ENABLED_1 = TimeOfUseEnabledEntry(address=274, key="timeofuse_enabled_1", name="Time of Use Enabled 1")
    TIMEOFUSE_ENABLED_2 = TimeOfUseEnabledEntry(address=275, key="timeofuse_enabled_2", name="Time of Use Enabled 2")
    TIMEOFUSE_ENABLED_3 = TimeOfUseEnabledEntry(address=276, key="timeofuse_enabled_3", name="Time of Use Enabled 3")
    TIMEOFUSE_ENABLED_4 = TimeOfUseEnabledEntry(address=277, key="timeofuse_enabled_4", name="Time of Use Enabled 4")
    TIMEOFUSE_ENABLED_5 = TimeOfUseEnabledEntry(address=278, key="timeofuse_enabled_5", name="Time of Use Enabled 5")
    TIMEOFUSE_ENABLED_6 = TimeOfUseEnabledEntry(address=279, key="timeofuse_enabled_6", name="Time of Use Enabled 6")

    BMS_CHARGING_VOLTAGE = BatteryVoltageEntry(address=312, key="bms_charging_voltage", name="BMS Charging Voltage", entity_registry_enabled_default=False)
    BMS_DISCHARGE_VOLTAGE = BatteryVoltageEntry(address=313, key="bms_discharge_voltage", name="BMS Discharge Voltage", entity_registry_enabled_default=False)
    BMS_CHARGE_CURRENT_LIMIT = CurrentEntry(address=314, key="bms_charge_current_limit", scale=1.0, data_type=DataType.UINT16, name="BMS Charge Current Limit", entity_registry_enabled_default=False)
    BMS_DISCHARGE_CURRENT_LIMIT = CurrentEntry(address=315, key="bms_discharge_current_limit", scale=1.0, data_type=DataType.UINT16, name="BMS Discharge Current Limit", entity_registry_enabled_default=False)
    BMS_SOC = SOCEntry(address=316, key="bms_soc", name="BMS SOC", entity_registry_enabled_default=False)
    BMS_VOLTAGE = BatteryVoltageEntry(address=317, key="bms_voltage", name="BMS Voltage", entity_registry_enabled_default=False)
    BMS_CURRENT = CurrentEntry(address=318, key="bms_current", scale=1.0, name="BMS Current", entity_registry_enabled_default=False)
    BMS_TEMP = TemperatureEntry(address=319, key="bms_temp", name="BMS Temperature", entity_registry_enabled_default=False)
