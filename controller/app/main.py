import asyncio
import logging
import os
import re

from .modbus_server import serve
from .mqtt_client import connect
from .state import TelemetryState


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    device_id = os.getenv("DEVICE_ID", "esp32-01")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,48}", device_id):
        raise ValueError("Invalid DEVICE_ID")
    state = TelemetryState(os.getenv("STATE_DB", "/data/state.sqlite"), device_id)
    client = connect(state)
    try:
        asyncio.run(serve(state))
    finally:
        client.disconnect()
        client.loop_stop()
        state.close()


if __name__ == "__main__":
    main()
