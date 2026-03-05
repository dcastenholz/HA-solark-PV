DOMAIN = "rtu_tcp_bridge"

# If you want a fixed serial port, set it here.
# Otherwise, leave as None so the bridge auto-creates a dedicated PTY.
DEFAULT_SERIAL_PORT = None

DEFAULT_BAUDRATE = 9600
DEFAULT_TCP_HOST = "10.0.0.20"
DEFAULT_TCP_PORT = 502

# PyModbus 3.11.2 uses `device_id`, not `unit_id`
DEFAULT_DEVICE_ID = 1

DEFAULT_REG_COUNT = 100