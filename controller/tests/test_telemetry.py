import json

import pytest

from app.alarms import Alarm
from app.state import TelemetryState
from app.validation import InvalidMeasurement


def payload(seq=1, timestamp=1000, temperature_c=25, ph=7.4, **extra):
    return json.dumps(dict(device_id="esp32-01", seq=seq, timestamp=timestamp,
                           temperature_c=temperature_c, ph=ph, **extra)).encode()


@pytest.fixture
def state(tmp_path):
    instance = TelemetryState(str(tmp_path / "state.sqlite"), "esp32-01")
    yield instance
    instance.close()


def test_startup_and_valid_measurement(state):
    assert state.registers(1000)[2:5] == [Alarm.STALE, 0, 65535]
    state.accept(payload(), now=1000)
    assert state.registers(1000) == [2500, 740, 0, 1, 0, 1]


@pytest.mark.parametrize("raw", [b"[]", b"null", b"{", b"\xff", b"x" * 1025,
    payload(seq=True), payload(temperature_c=True), payload(ph=float("nan")),
    payload(ph=float("inf")), payload(ph=15), payload(temperature_c=-127),
    payload(timestamp=960), payload(timestamp=1006), payload(unknown=1),
    payload(seq=-1), payload(temperature_c=10**400)])
def test_invalid_measurements(state, raw):
    with pytest.raises(InvalidMeasurement):
        state.accept(raw, now=1000)
    assert state.last is None


def test_replay_is_rejected_across_restart(tmp_path):
    path = str(tmp_path / "state.sqlite")
    first = TelemetryState(path, "esp32-01")
    first.accept(payload(), now=1000)
    first.close()
    second = TelemetryState(path, "esp32-01")
    try:
        assert second.registers(1000)[2] & Alarm.STALE
        with pytest.raises(InvalidMeasurement):
            second.accept(payload(), now=1000)
        second.accept(payload(seq=2, timestamp=1005), now=1005)
    finally:
        second.close()


def test_rejected_data_does_not_replace_last_good_reading(state):
    state.accept(payload(), now=1000)
    with pytest.raises(InvalidMeasurement, match="implausible_jump"):
        state.accept(payload(seq=2, timestamp=1005, ph=10), now=1005)
    state.reject()
    assert state.registers(1005)[0:4] == [2500, 740, Alarm.INVALID, 0]
    state.accept(payload(seq=3, timestamp=1010), now=1010)
    assert state.registers(1010)[2] == 0


def test_process_danger_is_distinct_from_unreliable_data(state):
    state.accept(payload(temperature_c=32, ph=9), now=1000)
    assert state.registers(1000)[2:4] == [Alarm.TEMPERATURE | Alarm.PH, 1]
    assert state.registers(1031)[2] & Alarm.STALE
    assert state.registers(1031)[3] == 0


def test_temperature_signed_encoding(state):
    state.accept(payload(temperature_c=-2), now=1000)
    assert state.registers(1000)[0] == 65336
