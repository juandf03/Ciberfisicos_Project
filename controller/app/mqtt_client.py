"""MQTT identity is bound to the allowed topic by the broker ACL."""
import logging
import os
from pathlib import Path

import paho.mqtt.client as mqtt

from .validation import InvalidMeasurement

LOG = logging.getLogger(__name__)


def connect(state):
    topic = f"farm/{state.device_id}/telemetry"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="farm-controller")
    client.username_pw_set("controller", Path(os.environ["MQTT_PASSWORD_FILE"]).read_text().strip())
    client.tls_set(ca_certs=os.environ["MQTT_CA_FILE"])
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            LOG.error("MQTT authentication/connection rejected: %s", reason_code)
        else:
            client.subscribe(topic, qos=1)
            LOG.info("MQTT connected; subscribed to %s", topic)

    def on_message(client, userdata, message):
        if message.topic != topic:
            return
        try:
            if message.retain:
                raise InvalidMeasurement("retained_telemetry")
            reading = state.accept(message.payload)
            LOG.info("Accepted device=%s seq=%s temperature=%.2f ph=%.2f",
                     reading.device_id, reading.seq, reading.temperature_c, reading.ph)
        except InvalidMeasurement as exc:
            state.reject()
            LOG.warning("Rejected telemetry: %s", exc)
        except Exception:
            state.reject()
            LOG.exception("Could not persist/process telemetry")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(os.getenv("MQTT_HOST", "mosquitto"), 8883, keepalive=30)
    client.loop_start()
    return client
