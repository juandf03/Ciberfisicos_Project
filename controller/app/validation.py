"""Strict telemetry validation; physical limits differ from process alarms."""
import json
import math
from dataclasses import dataclass


class InvalidMeasurement(ValueError):
    pass


@dataclass(frozen=True)
class Measurement:
    device_id: str
    seq: int
    timestamp: float
    temperature_c: float
    ph: float


def parse_measurement(payload: bytes, device_id: str, now: float) -> Measurement:
    if len(payload) > 1024:
        raise InvalidMeasurement("payload_too_large")
    try:
        obj = json.loads(payload)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise InvalidMeasurement("invalid_json") from exc
    required = {"device_id", "seq", "timestamp", "temperature_c", "ph"}
    if not isinstance(obj, dict) or set(obj) != required:
        raise InvalidMeasurement("invalid_schema")
    if obj["device_id"] != device_id:
        raise InvalidMeasurement("wrong_device")
    if type(obj["seq"]) is not int or not 0 <= obj["seq"] <= 2**63 - 1:
        raise InvalidMeasurement("invalid_sequence")
    for name in ("timestamp", "temperature_c", "ph"):
        value = obj[name]
        if type(value) not in (int, float):
            raise InvalidMeasurement("invalid_number")
        try:
            finite = math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise InvalidMeasurement("invalid_number")
    if not -5 <= now - obj["timestamp"] <= 30:
        raise InvalidMeasurement("stale_or_future_timestamp")
    if not -10 <= obj["temperature_c"] <= 60 or not 0 <= obj["ph"] <= 14:
        raise InvalidMeasurement("sensor_out_of_range")
    return Measurement(**obj)


def check_transition(current: Measurement, previous: Measurement | None) -> None:
    if previous is None:
        return
    if current.seq <= previous.seq or current.timestamp <= previous.timestamp:
        raise InvalidMeasurement("replay_or_out_of_order")
    # After a long interruption, establish a new baseline; still enforce replay checks.
    elapsed = current.timestamp - previous.timestamp
    if elapsed <= 60 and (
        abs(current.temperature_c - previous.temperature_c) > 0.5 * elapsed + 1
        or abs(current.ph - previous.ph) > 0.05 * elapsed + 0.2
    ):
        raise InvalidMeasurement("implausible_jump")
