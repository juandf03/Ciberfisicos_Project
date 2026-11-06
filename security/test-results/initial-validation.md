# Verificación inicial — 2026-11-06

Entorno: Windows, Python 3.12; sin Docker Engine disponible.

| Comprobación | Resultado |
|---|---|
| `python -m pytest -q` | 22 pruebas superadas |
| JSON, tipos, NaN/Inf, frescura, límites físicos | Superado |
| Replay persistente tras reinicio | Superado |
| Saltos improbables y conservación de última lectura válida | Superado |
| Alarmas de proceso diferenciadas de calidad y ausencia | Superado |
| Modbus TCP real: FC04, offset cero y rechazo de escritura/holding/fuera de mapa | Superado en loopback |
| `python -m compileall -q controller/app simulator` | Superado |
| `bash -n scripts/init-lab.sh` | Superado |
| `bash -n scripts/verify-pipeline.sh` | Superado |
| Firmware PlatformIO `esp32dev` (credenciales ficticias) | Compilado: RAM 46416/327680 bytes; flash 906497/1310720 bytes |
| YAML Compose e invariantes de red/puerto Modbus | Superado con PyYAML |
| `docker compose config` y arranque de contenedores | Pendiente: Docker no disponible |
| TLS real, autenticación y ACL Mosquitto | Pendiente de despliegue |
| ScadaBR: arranque, persistencia, puntos, dashboard y roles | Pendiente de despliegue |
| Sensores y ESP32 físicos | Pendiente de montaje/calibración |

WAR oficial ScadaBR 1.2 descargado localmente, excluido de Git:

- Origen: https://github.com/ScadaBR/ScadaBR/releases/download/v1.2/ScadaBR.war
- SHA256: `a895a8f2e8d4b36bf8c8292dae9ebb30ed04cf4cb27b6c53b9634c4d8f0b80e2`
- Se ha inspeccionado `WEB-INF/classes/env.properties`: Derby, propiedad `db.url`
  con ruta de base de datos. La imagen usa ruta absoluta en volumen persistente.

Este registro describe comprobaciones realizadas, no acredita seguridad de
producción ni sustituye las pruebas de integración sobre Debian.

La compilación Xtensa en Windows necesitó una unidad temporal sin espacios
apuntando al repositorio, porque la ruta local de herramientas contenía espacios.
La unidad se eliminó al terminar. Se observaron advertencias de directivas
`#undef` en la dependencia OneWire, sin impedir compilar. El binario usa
credenciales ficticias y no se ha grabado en hardware.

El workflow incluye una prueba Docker del flujo TLS y el watchdog. Su ejecución
queda pendiente de GitHub Actions o de la VM Debian; no se ha ejecutado localmente.
