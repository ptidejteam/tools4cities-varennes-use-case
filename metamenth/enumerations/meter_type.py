from metamenth.enumerations.abstract_enum import AbstractEnum


class MeterType(AbstractEnum):
    """
    Different types of meters used in a building_structure.

    Author: Peter Yefi
    Email: peteryefi@gmail.com
    """
    ELECTRICITY = "Electricity"
    CHARGE_DISCHARGE = "ChargeDischarge"
    POWER = "Power"
    FLOW = "Flow"
    HEAT = "Heat"
    GAS = "Gas"

