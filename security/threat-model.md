# Modelo de amenazas del laboratorio

Activos: integridad/frescura de medidas, credenciales, disponibilidad, histórico,
configuración HMI y código. Límites de confianza: dispositivo → Wi-Fi → broker,
broker → controlador, controlador → SCADA, administrador → Debian/GitHub.

| Amenaza | Mitigación implementada | Riesgo residual |
|---|---|---|
| Interceptación y servidor falso | TLS, CA privada de laboratorio y verificación de nombre | Compromiso de CA/ESP32 |
| Dispositivo no autorizado | Credencial por identidad y ACL vinculada al topic | Credencial robada permite publicar como ese nodo |
| Repetición/desorden | Secuencia persistente y timestamp fresco | Reloj/NVS comprometidos; restauración de copias antiguas |
| Medidas manipuladas | Esquema, rangos físicos y saltos plausibles | Datos falsos pero plausibles de un dispositivo comprometido |
| Pérdida de conectividad | Calidad 0 y alarma por falta de datos | Denegación de servicio sigue siendo posible |
| Escrituras Modbus | FC04, rechazo de escrituras y red interna | Acceso root Docker supera el aislamiento |
| Toma del SCADA | Loopback/túnel SSH; roles a configurar | ScadaBR y dependencias requieren revisión |
| Firmware manipulado | Fuera del alcance inicial: Secure Boot/flash encryption | Acceso físico y extracción de secretos |

No hay actuadores: las alarmas apoyan supervisión, no control automático ni un
sistema de seguridad funcional. Un atacante local privilegiado puede acceder a
volúmenes y secretos. mTLS, firmware firmado y rotación automatizada quedan como
mejoras, no se declaran implementados.
