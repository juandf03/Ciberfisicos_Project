"""Demonstration thresholds, to be tuned to species and instrumentation."""
from enum import IntFlag


class Alarm(IntFlag):
    NONE = 0
    TEMPERATURE = 1
    PH = 2
    INVALID = 4
    STALE = 8


def process_alarms(temperature_c: float, ph: float) -> Alarm:
    alarm = Alarm.NONE
    if not 20 <= temperature_c <= 30:
        alarm |= Alarm.TEMPERATURE
    if not 6.5 <= ph <= 8.5:
        alarm |= Alarm.PH
    return alarm
