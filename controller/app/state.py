"""Persist accepted telemetry before publishing it to Modbus."""
import sqlite3
import threading
import time
from pathlib import Path

from .alarms import Alarm, process_alarms
from .validation import Measurement, check_transition, parse_measurement


class TelemetryState:
    def __init__(self, database: str, device_id: str):
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        self.device_id = device_id
        self.lock = threading.RLock()
        self.db = sqlite3.connect(database, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS readings (device_id TEXT PRIMARY KEY, "
                        "seq INTEGER, timestamp REAL, temperature_c REAL, ph REAL)")
        row = self.db.execute("SELECT * FROM readings WHERE device_id=?", (device_id,)).fetchone()
        self.last = Measurement(*row) if row else None
        self.invalid = False
        self.received_at = None

    def accept(self, payload: bytes, now: float | None = None) -> Measurement:
        now = time.time() if now is None else now
        with self.lock:
            reading = parse_measurement(payload, self.device_id, now)
            check_transition(reading, self.last)
            with self.db:
                self.db.execute("INSERT OR REPLACE INTO readings VALUES (?, ?, ?, ?, ?)",
                                (reading.device_id, reading.seq, reading.timestamp,
                                 reading.temperature_c, reading.ph))
            self.last = reading
            self.invalid = False
            self.received_at = time.monotonic()
            return reading

    def reject(self):
        with self.lock:
            self.invalid = True

    def registers(self, now: float | None = None) -> list[int]:
        now = time.time() if now is None else now
        with self.lock:
            alarm = Alarm.INVALID if self.invalid else Alarm.NONE
            age = 65535 if self.last is None else min(65535, max(0, int(now - self.last.timestamp)))
            if (self.last is None or self.received_at is None or age > 30
                    or time.monotonic() - self.received_at > 30):
                alarm |= Alarm.STALE
            if self.last is None:
                return [0, 0, int(alarm), 0, age, 0]
            alarm |= process_alarms(self.last.temperature_c, self.last.ph)
            reliable = not (alarm & (Alarm.INVALID | Alarm.STALE))
            return [round(self.last.temperature_c * 100) & 0xFFFF,
                    round(self.last.ph * 100), int(alarm), int(reliable), age,
                    self.last.seq & 0xFFFF]

    def close(self):
        self.db.close()
