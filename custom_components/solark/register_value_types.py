import datetime
from typing import Union

NumericValue = Union[int, float]
SensorValue = Union[int, float, str, datetime.datetime, None]
RegisterValue = Union[int, str]
