from .data import SolArkData

from .device_info import SolArkDeviceInfo
from homeassistant.core import HomeAssistant

class DatChangeHandlers():
    _runtime_data: SolArkData

    def __init__(self, runtime_data: SolArkData):
        self._runtime_data = runtime_data

    def SN_change_handler(self, new_serial_number, old_serial_number):
        SolArkDeviceInfo.set_serial_number(self._runtime_data, new_serial_number)
