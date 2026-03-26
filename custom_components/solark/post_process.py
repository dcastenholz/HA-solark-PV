
@staticmethod
def get_mppt_info_string(decimal_number: int) -> str:
    info: tuple[int, int] = get_mppt_info(decimal_number)
    info_string: str = f"{info[0]} MPPTs, {info[1]} phase"
    return info_string

@staticmethod
def get_mppt_info(decimal_number: int) -> tuple[int, int]:
    hex_tuple: tuple[str, ...] = decimal_to_hex_tuple(decimal_number)
    info: tuple[int, int] = combine_decimal_digits(hex_tuple[0], hex_tuple[1]), combine_decimal_digits(hex_tuple[2], hex_tuple[3])
    return info

@staticmethod
def get_firmware(decimal_number: int) -> str:
    hex_tuple: tuple[str, ...] = decimal_to_hex_tuple(decimal_number)
    firmware: str = f"{hex_tuple[0]}.{hex_tuple[1]}.{hex_tuple[2]}.{hex_tuple[3]}"
    return firmware

@staticmethod
def decimal_to_hex_tuple(decimal_number: int) -> tuple[str, ...]:
    # Convert to hex without the '0x' prefix and make uppercase
    hex_str = hex(decimal_number)[2:].upper()
    # Create a tuple with each hex digit as a string
    return tuple(hex_str)

@staticmethod
def combine_decimal_digits(a: int, b: int) -> int:
    return a * 10 + b