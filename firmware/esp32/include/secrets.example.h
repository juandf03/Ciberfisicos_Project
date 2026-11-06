#pragma once
// Copy to secrets.h (ignored by Git) and replace all placeholders.
#define WIFI_SSID "CHANGE_ME"
#define WIFI_PASSWORD "CHANGE_ME"
// Use the IP passed to init-lab.sh, or a DNS name included in the certificate SAN.
#define MQTT_HOST "192.168.1.50"
#define MQTT_PASSWORD "CHANGE_ME"
#define DEVICE_ID "esp32-01"
static const char MQTT_CA[] = R"CERT(
-----BEGIN CERTIFICATE-----
REPLACE_WITH_CONTENT_OF_infrastructure/certs/ca.crt
-----END CERTIFICATE-----
)CERT";
