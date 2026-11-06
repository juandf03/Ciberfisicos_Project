"""Publish smooth synthetic water readings, with a persistent sequence counter."""
import json
import math
import os
import threading
import time
from pathlib import Path

import paho.mqtt.client as mqtt


def main():
    device_id = os.getenv("DEVICE_ID", "esp32-01")
    sequence_file = Path(os.getenv("SEQUENCE_FILE", "simulator/.sequence"))
    sequence_file.parent.mkdir(parents=True, exist_ok=True)
    seq = int(sequence_file.read_text()) if sequence_file.exists() else 0
    connected = threading.Event()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sim-{device_id}")
    client.username_pw_set(device_id, Path(os.environ["MQTT_PASSWORD_FILE"]).read_text().strip())
    client.tls_set(ca_certs=os.environ["MQTT_CA_FILE"])

    def on_connect(client, userdata, flags, reason_code, properties):
        if not reason_code.is_failure:
            connected.set()

    def on_disconnect(client, userdata, flags, reason_code, properties):
        connected.clear()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(1, 30)
    client.connect_async(os.getenv("MQTT_HOST", "mosquitto"), 8883, 30)
    client.loop_start()
    try:
        while True:
            if not connected.wait(5):
                continue
            seq += 1
            # Persist before publishing, so a restart never reuses a sequence.
            temporary = sequence_file.with_suffix(".tmp")
            temporary.write_text(str(seq))
            temporary.replace(sequence_file)
            now = time.time()
            payload = {"device_id": device_id, "seq": seq, "timestamp": now,
                       "temperature_c": round(25 + math.sin(now / 120), 2),
                       "ph": round(7.4 + 0.1 * math.sin(now / 180), 2)}
            result = client.publish(f"farm/{device_id}/telemetry", json.dumps(payload), qos=1, retain=False)
            result.wait_for_publish(timeout=10)
            print(json.dumps(payload), flush=True)
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
