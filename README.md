# Ciberfisicos_Project

Laboratorio de ciberseguridad industrial IIoT/SCADA: una piscifactoría inteligente
con ESP32, sensores de temperatura y pH y **ScadaBR clásico 1.2**.

Flujo: sensores → ESP32 → MQTT con TLS → Mosquitto → controlador Python →
Modbus TCP en red interna Docker → ScadaBR. Un simulador permite empezar sin
sensores. Debian 13 en VMware sustituye al controlador físico Raspberry Pi.

## Empezar

Seguir [instalación en Debian](docs/setup.md), después
[configuración de ScadaBR](docs/scadabr.md) y [montaje ESP32](docs/hardware.md).

```bash
cp .env.example .env
# Ajustar IP LAN y DEVICE_ID en .env antes de generar credenciales.
sudo bash scripts/init-lab.sh IP_DEBIAN
sudo docker compose --env-file .env -f infrastructure/compose.yaml --profile simulation up -d --build
```

Para la HMI, descargar el WAR oficial según `docs/scadabr.md` y añadir
`--profile scada` al comando Compose. Acceso por túnel SSH a
`http://localhost:8080/ScadaBR/`. No se requiere Scada-LTS.

## Contenido

| Directorio | Responsabilidad |
|---|---|
| `firmware/esp32/` | PlatformIO, DS18B20, ADC1 para pH, TLS y secuencia NVS |
| `controller/` | Validación, alarmas, persistencia, cliente MQTT y servidor Modbus |
| `infrastructure/` | Compose, broker, certificados locales e imagen propia ScadaBR |
| `simulator/` | Emisor MQTT de datos sintéticos con secuencia persistente |
| `security/` | Modelo de amenazas, controles y resultados |
| `docs/` | Arquitectura, contrato de datos, instalación y hardware |
| `.github/workflows/` | Pruebas Python, validación Compose y compilación ESP32 |

Consultar el [contrato MQTT y mapa Modbus](docs/architecture.md) y la
[estrategia de ramas y PR](CONTRIBUTING.md).

## Estado y siguientes hitos

La base de código permite desarrollar controlador, hardware y supervisión por
separado. Las verificaciones ejecutadas y sus límites constan en
[resultados iniciales](security/test-results/initial-validation.md).

- [x] Arquitectura y estructura de repositorio.
- [x] Controlador, simulador y configuraciones de seguridad iniciales.
- [ ] Instalar/verificar la VM Debian y Docker.
- [ ] Arrancar ScadaBR clásico y configurar puntos virtuales/Modbus, roles y dashboard.
- [ ] Calibrar sensores y probar el ESP32 físico.
- [ ] Recoger evidencias TLS, ACL, alarmas y acceso HMI con el conjunto desplegado.
- [ ] Confirmar privacidad, colaboradores y protección de ramas en GitHub.

No versionar `.env`, `secrets.h`, contraseñas, claves, bases de datos ni WAR.
Los umbrales de alarma son demostrativos. Secure Boot y cifrado de flash se
documentan como mejoras; no se modifican eFuses desde este repositorio.
