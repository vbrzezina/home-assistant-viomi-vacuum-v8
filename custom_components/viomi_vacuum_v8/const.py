"""Constants for the Viomi Vacuum V8 integration."""

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN

DOMAIN = "viomi_vacuum_v8"
DATA_KEY = DOMAIN
DEFAULT_NAME = "Viomi Vacuum V8"

ALL_PROPS = [
    "run_state",
    "mode",
    "err_state",
    "battary_life",
    "box_type",
    "mop_type",
    "s_time",
    "s_area",
    "suction_grade",
    "water_grade",
    "remember_map",
    "has_map",
    "is_mop",
    "has_newmap",
    "hw_info",
    "sw_info",
    "start_time",
    "order_time",
    "v_state",
    "zone_data",
    "repeat_state",
    "light_state",
    "is_charge",
    "is_work",
]

VACUUM_CARD_PROPS_REFERENCES = {
    "cleaned_area": "s_area",
    "cleaning_time": "s_time",
}

FAN_SPEEDS = {
    "Silent": 0,
    "Standard": 1,
    "Medium": 2,
    "Turbo": 3,
}

WATER_LEVELS = {
    "Low": 11,
    "Medium": 12,
    "High": 13,
}

CLEANING_MODES = {
    0: "Vacuum",
    1: "Vacuum & Mop",
    2: "Mop",
    3: "Zone",
    4: "Spot",
}

BOX_TYPES = {
    0: "No Bin",
    1: "Vacuum",
    2: "Water",
    3: "Vacuum & Water",
}

CONF_HOST = CONF_HOST
CONF_TOKEN = CONF_TOKEN
CONF_NAME = CONF_NAME