"""Constants for the NECTOR200 integration."""
DOMAIN = "nector200"
DEFAULT_NAME = "NECTOR200"
DEFAULT_SCAN_INTERVAL = 30

# API Response Keys
KEY_TEMP = "temp"
KEY_SETPOINT = "sttmp"
KEY_STANDBY = "stby"
KEY_LIGHT = "ligh"
KEY_DEFROST = "def"
KEY_ALARM = "almst"
KEY_RECORDING = "recst"
KEY_BG_TEMP = "bg_temp"

# Button indices for btnfunct.cgi
BTN_STANDBY = 0
BTN_LIGHT = 1
BTN_DEFROST = 2

# Parameter levels for pdatamod.cgi
PARAM_LEVEL_SETPOINT = 0
PARAM_LEVEL_1 = 1
PARAM_LEVEL_2 = 2
PARAM_LEVEL_3 = 3
PARAM_LEVEL_4 = 4

# Parameter operation types
PARAM_OP_UPDATE = "upd"
PARAM_OP_MODIFY = "mod"

# Authentication
DEFAULT_USERNAME = "admin"
SESSION_KEEPALIVE_INTERVAL = 90  # seconds (under 2 minute limit)