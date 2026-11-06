# Controles y evidencias

| Control | Implementación | Verificación |
|---|---|---|
| MQTT cifrado | Solo listener 8883, TLS mínimo 1.2 | Captura autorizada y conexión con CA incorrecta |
| Autenticación | Hashes Mosquitto, secretos fuera de Git | Intentar conectar con contraseña errónea |
| ACL | El usuario solo escribe `farm/<usuario>/telemetry` | Intentar escribir un topic ajeno y comprobar que no llega |
| Validación | JSON estricto, finitud, límites, saltos | pytest y envío de datos anómalos en la maqueta |
| Antirrepetición | SQLite + NVS/contador persistente simulador | pytest y repetir tras reinicio |
| Calidad | INVALID y STALE, sin reemplazar último válido | pytest y detener el emisor >30 s |
| Aislamiento industrial | Puerto 1502 sin publicación Docker | `docker compose config`, revisar puertos desde host |
| Solo lectura | FC04; rechazo de otras funciones | Prueba Modbus por TCP real |
| Mínimo privilegio | Usuarios sin root, capacidades eliminadas, FS de solo lectura | Inspeccionar contenedores en Debian |
| Acceso HMI | Loopback y túnel SSH | Configurar roles y probar con usuarios reales |
| CI | Python, Compose y compilación firmware | Revisar ejecución en GitHub Actions |

Guardar fecha, entorno, comando, resultado esperado, observado y evidencia en
`test-results/`. No registrar contraseñas ni claves privadas. Una prueba pendiente
no es un control demostrado. Las pruebas activas se limitan a la maqueta propia.
