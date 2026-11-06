#include <Arduino.h>
#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <time.h>
#include "secrets.h"

constexpr uint8_t TEMPERATURE_PIN = 4;
constexpr uint8_t PH_PIN = 34; // ADC1, compatible with Wi-Fi on classic ESP32.
// Replace with coefficients from calibration using buffer solutions.
constexpr float PH_SLOPE = -5.7f;
constexpr float PH_INTERCEPT = 21.34f;
constexpr bool PH_CALIBRATED = false; // Explicitly enable after calibration.
OneWire oneWire(TEMPERATURE_PIN);
DallasTemperature temperature(&oneWire);
WiFiClientSecure tls;
PubSubClient mqtt(tls);
Preferences preferences;
uint64_t sequence = 0;
uint64_t reservedUntil = 0;
unsigned long lastPublish = 0;
unsigned long lastConnect = 0;

uint64_t nextSequence() {
  // Reserve batches to avoid a flash write every five seconds. After a reboot,
  // unused numbers are skipped. NVS failure stops publishing to prevent replay.
  if (sequence >= reservedUntil) {
    reservedUntil = sequence + 1000;
    if (preferences.putULong64("reserved", reservedUntil) != sizeof(uint64_t)) {
      Serial.println("NVS failure: stopping telemetry");
      while (true) delay(1000);
    }
  }
  return ++sequence;
}

void setup() {
  Serial.begin(115200);
  temperature.begin();
  analogSetPinAttenuation(PH_PIN, ADC_11db);
  if (!preferences.begin("farm", false)) {
    Serial.println("Cannot open NVS");
    while (true) delay(1000);
  }
  sequence = preferences.getULong64("reserved", 0);
  reservedUntil = sequence;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  tls.setCACert(MQTT_CA);
  mqtt.setServer(MQTT_HOST, 8883);
  mqtt.setBufferSize(1024);
  mqtt.setSocketTimeout(5);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED || time(nullptr) < 1735689600) {
    delay(100);
    return;
  }
  if (!mqtt.connected()) {
    if (millis() - lastConnect >= 5000) {
      lastConnect = millis();
      mqtt.connect(DEVICE_ID, DEVICE_ID, MQTT_PASSWORD);
    }
    delay(10);
    return;
  }
  mqtt.loop();
  if (millis() - lastPublish < 5000) return;
  lastPublish = millis();
  temperature.requestTemperatures();
  const float celsius = temperature.getTempCByIndex(0);
  if (!PH_CALIBRATED || celsius == DEVICE_DISCONNECTED_C || celsius == 85.0f) {
    Serial.println("Telemetry withheld: calibrate pH/check temperature sensor");
    return; // Controller raises stale-data alarm; never invent a sensor reading.
  }
  uint32_t millivolts = 0;
  for (int i = 0; i < 16; ++i) {
    millivolts += analogReadMilliVolts(PH_PIN);
    delay(2);
  }
  const float voltage = millivolts / 16000.0f;
  const float ph = PH_SLOPE * voltage + PH_INTERCEPT;
  if (ph < 0 || ph > 14 || celsius < -10 || celsius > 60) {
    Serial.println("Telemetry withheld: invalid physical reading");
    return;
  }
  JsonDocument data;
  data["device_id"] = DEVICE_ID;
  data["seq"] = nextSequence();
  data["timestamp"] = static_cast<int64_t>(time(nullptr));
  data["temperature_c"] = celsius;
  data["ph"] = ph;
  char payload[384];
  serializeJson(data, payload, sizeof(payload));
  String topic = String("farm/") + DEVICE_ID + "/telemetry";
  // PubSubClient publishes QoS 0; loss is detected by the controller timeout.
  if (!mqtt.publish(topic.c_str(), payload, false)) Serial.println("Publish failed");
}
