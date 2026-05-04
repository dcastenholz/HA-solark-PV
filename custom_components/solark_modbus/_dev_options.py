''' This file contains any design time or debug time manipulations.'''

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config.config_data import ConfigData

USE_TEST_CONFIG_VALUES: bool = True


class DevOptions_ConfigData_DebugValues():  # pylint: disable=invalid-name
    '''Insert debugging values into the config data.'''
    @staticmethod
    def modify_config_data_with_debug_values_v1(config_data: "ConfigData") -> None:
        '''Insert debugging values into the config data.'''
        if not USE_TEST_CONFIG_VALUES:
            return

        config_data.scan_interval = 10
        config_data.max_stale_data_age_seconds = 30
        config_data.tcp_host = "10.0.0.20"
